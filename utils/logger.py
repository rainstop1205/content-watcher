import logging
import os
from logging.handlers import TimedRotatingFileHandler # <--- 改用這個

def setup_logger():
    # 確保 logs 資料夾存在
    os.makedirs("logs", exist_ok=True)

    logger = logging.getLogger("content_watcher")
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    # 使用「時間」來切分 Log
    file_handler = TimedRotatingFileHandler(
        filename="logs/app.log",
        when="midnight",    # 每天午夜 00:00 切換
        interval=1,         # 每 1 天切一次
        backupCount=7,      # 只保留最近 7 個檔案 (7天後自動刪除舊的)
        encoding="utf-8"
    )
    
    # 修改檔名後綴格式 (被切走的舊檔名變成 app.log.2026-01-25)
    file_handler.suffix = "%Y-%m-%d"
    file_handler.setLevel(logging.DEBUG)

    # Console 只顯示 INFO 以上
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "[%(asctime)s][%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger