import requests
import time
import logging
from .base import BaseNotifier
from utils.logger import setup_logger

logger = logging.getLogger(__name__)

class DiscordNotifier(BaseNotifier):
    def send(self, messages: list[str]):
        # 1. 從設定檔取得 Webhook URL
        webhook_url = self.config.get('webhook_url')
        
        if not webhook_url:
            logger.error("[Error] Discord Notifier 未設定 webhook_url")
            return

        if not messages:
            return

        logger.info(f" -> [Discord] 準備發送 {len(messages)} 則通知...")

        # 2. 逐條發送 (Batch Loop)
        for msg in messages:
            payload = {
                "content": msg
            }

            try:
                # 設定 timeout 避免網路卡死
                response = requests.post(webhook_url, json=payload, timeout=10)
                
                # 檢查 HTTP Status Code (4xx, 5xx 會噴錯)
                response.raise_for_status()
                
                # 為了版面乾淨，只印出訊息前 20 字
                preview = msg.replace('\n', ' ')[:20]
                logger.info(f"    [Sent] {preview}...")

            except requests.exceptions.HTTPError as e:
                # 特別抓出 429 (Too Many Requests)
                if e.response.status_code == 429:
                    logger.warning(f"[429: Too Many Requests] 發太快了！Discord 要求冷靜一下。")
                    # 通常 header 會有 retry-after，這裡簡單睡久一點
                    time.sleep(5)
                else:
                    logger.error(f"發送失敗 (HTTP {e.response.status_code}): {e}")
            
            except Exception as e:
                logger.error(f"發送發生未知錯誤: {e}")

            # 每發送一則就強制休息，避免觸發 Rate Limit
            time.sleep(1.0)