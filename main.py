import time
import json
import os
import sys
import tempfile
from sources.ptt import PTTSource
from notifiers.discord import DiscordNotifier
from utils.matcher import is_interested
from utils.logger import setup_logger

logger = setup_logger()
HISTORY_FILE = 'history.json'

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)
    
def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list): return data
        except: pass
    return []

def save_history(history_list):
    keep_list = history_list[-2000:] # List 才有順序，這樣 [-2000:] 砍掉的才是真的「舊資料」
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(keep_list, f)

# Singleton 模式
def run_single_instance():
    lock_file = os.path.join(tempfile.gettempdir(), "content_watcher.lock")
    try:
        if os.path.exists(lock_file):
            try:
                os.remove(lock_file)
            except OSError:
                print("⚠️ 程式已經在執行中！")
                return
        f = open(lock_file, 'w')
        f.write(f"PID: {os.getpid()}")
    except Exception as e:
        print(f"Lock error: {e}")
    
    try:
        main()
    finally:
        try:
            f.close()
            os.remove(lock_file)
        except: pass

def main():
    logger.info("🚀 Content Watcher 啟動中")
    
    # 這裡的 history 代表「已經通知過」的文章
    history_list = load_history()
    notified_ids = set(history_list) 
    
    try:
        initial_config = load_config()
    except FileNotFoundError:
        logger.error("找不到 config.json！請確認檔案是否存在。")
        return
    except json.JSONDecodeError:
        logger.error("config.json 格式錯誤！請檢查 JSON 語法。")
        return

    notifiers = [DiscordNotifier(n) for n in initial_config.get('notifiers', []) if n['type'] == 'discord']

    logger.info("初始化完成，開始監控內容...")

    while True:
        try:
            # 熱重載 Config
            config = load_config()
            messages = []
            
            logger.debug("Starting new scan cycle...")

            # 用來避免「單次掃描中」重複處理同一篇文章
            current_scan_processed = set()

            # 取得 sources 設定
            sources_conf = config.get('sources', {})

            # PTT 區塊
            if 'ptt' in sources_conf:
                for board_conf in sources_conf['ptt']:
                    if not board_conf.get('enable', True): continue
                    
                    runner = PTTSource(board_conf)
                    posts = runner.fetch_new_posts()
                    
                    for post in posts:
                        p_id = post['id']
                        
                        # 1. 如果「已經通知過」就不再通知
                        if p_id in notified_ids: continue
                        
                        # 2. 本輪掃描去重
                        if p_id in current_scan_processed: continue
                        current_scan_processed.add(p_id)
                        
                        # 3. 檢查是否感興趣 (關鍵字及推文數)
                        if is_interested(post, board_conf, config.get('global_settings', {})):
                            
                            # 如果是爆文，前面加個火
                            msg_prefix = "🔥" if post['push_count'] > 99 else ""
                            title = f"{post['title']}".strip()
                            msg = f"{msg_prefix}**[PTT] {post['board']} 版** {title}\n{post['link']}"
                            
                            logger.info(f"{msg} (推:{post['push_count']})")
                            messages.append(msg)
                            
                            # 只有在通知後才加入歷史清單
                            notified_ids.add(p_id)
                            history_list.append(p_id)
            
            # 2. 未來增加處理 XXX 區塊
            # if 'XXX' in sources_conf:
            #     for forum_conf in sources_conf['XXX']:
            #          ...

            if messages:
                logger.info(f"準備發送 {len(messages)} 則通知...")
                for notifier in notifiers:
                    notifier.send(messages)
                # 發送成功後才存檔
                save_history(history_list)
            else:
                logger.debug("No new notifications this cycle.")

            time.sleep(config.get('scan_interval', 30))

        except Exception as e:
            logger.exception("主流程發生 Critical Error")
            time.sleep(60)

if __name__ == "__main__":
    run_single_instance()