import logging
import requests
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from .base import BaseSource

logger = logging.getLogger(__name__)

class PTTSource(BaseSource):
    def __init__(self, config):
        super().__init__(config)
        # 初始化 Session (讓爬蟲更穩定)
        self.session = requests.Session()
        
        # 設定重試機制 (如果失敗，會自動重試 3 次)
        retries = Retry(
            total=3,
            backoff_factor=1, # 失敗後等待 1s, 2s, 4s...
            status_forcelist=[500, 502, 503, 504]
        )
        # 把重試機制掛載到 https:// 開頭的網址
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
    
    def _parse_article_list(self, soup, board):
        """把解析邏輯抽出來，主程式(fetch_new_posts)比較乾淨"""
        posts = []
        # 1. 找到主容器
        main_container = soup.find("div", class_="r-list-container")
        if not main_container: return []

        for div in main_container.find_all("div", recursive=False):
            # 只要讀到這個 class，代表後面都是置底文，直接 break (通常只有 index.html 會有這條線，上一頁沒有)
            if "r-list-sep" in div.get("class", []):
                break
            # 確保是文章區塊 (r-ent)
            if "r-ent" not in div.get("class", []): continue

            title_div = div.find("div", class_="title")
            if title_div and title_div.a:
                title = title_div.a.text.strip()
                href = title_div.a['href']
                link = "https://www.ptt.cc" + href
                post_id_raw = href.split('/')[-1].replace('.html', '')
                unique_id = f"PTT-{board}-{post_id_raw}"

                # 解析推文數
                push_count = 0
                nrec_div = div.find("div", class_="nrec")
                if nrec_div:
                    span = nrec_div.find("span")
                    if span:
                        push_str = span.text.strip()
                        if push_str == '爆': push_count = 100
                        elif push_str.startswith('X'): push_count = -10 
                        elif push_str.isdigit(): push_count = int(push_str)

                posts.append({
                    'id': unique_id,
                    'title': title,
                    'link': link,
                    'source': f"PTT-{board}",
                    'board': board,
                    'push_count': push_count
                })
        return posts

    def fetch_new_posts(self):
        board = self.config.get('board_name')
        max_pages = self.config.get('scan_pages', 1) # 預設只爬 1 頁 (即 index.html)

        if not board:
            return []

        # 起始入口
        url = f"https://www.ptt.cc/bbs/{board}/index.html"
        # 設定 Cookie (通過 18 歲驗證)
        cookies = {'over18': '1'}
        # 偽裝成最新的 Chrome 瀏覽器
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.ptt.cc/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
        }

        all_posts = []
        current_page = 0
        # === 迴圈：往回爬 N 頁 ===
        while current_page < max_pages and url:
            try:
                # 為了避免對 PTT 造成負擔，每爬一頁稍作停頓 (尤其是爬多頁時)
                if current_page > 0:
                    time.sleep(0.5)

                logger.debug(f"[{board}]正在爬第 {current_page + 1} 頁: {url}")
                resp = self.session.get(url, headers=headers, cookies=cookies, timeout=10)
                
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    
                    # 1. 解析文章列表
                    posts_in_page = self._parse_article_list(soup, board)
                    all_posts.extend(posts_in_page) # 加入總清單

                    # 2. 找出「上一頁」的網址，準備下一輪迴圈
                    paging_div = soup.find("div", class_="btn-group btn-group-paging")
                    if paging_div:
                        # PTT 的按鈕順序通常是: 最舊 | 上頁 | 下頁 | 最新
                        # 上頁通常是第二個按鈕 (index 1)
                        links = paging_div.find_all("a")
                        prev_link = None
                        
                        for link in links:
                            if "上頁" in link.text:
                                prev_link = link['href']
                                break
                        
                        if prev_link:
                            url = "https://www.ptt.cc" + prev_link
                        else:
                            url = None # 找不到上一頁(已到第一頁)，結束
                    else:
                        url = None

                    current_page += 1
                else:
                    logger.warning(f"PTT {board} 回傳異常: {resp.status_code}")
                    break
            except requests.exceptions.RequestException as e:
                # 只抓 Request 相關錯誤，避免洗版
                logger.error(f"抓取 PTT {board} 版連線失敗: {e}")
            except Exception as e:
                logger.error(f"抓取 PTT {board} 版發生未預期錯誤: {e}")
                break

        return all_posts