# 🚀 Content Watcher

可擴充、高彈性的網路爬蟲機器人。
專門追蹤「即時情報」、「限時免費」或「熱門貼文」。
目前版本(v1.0)完整支援 PTT，並透過 Discord 發送即時通知。

## ✨ 特色 (Features)

### 核心功能
* **模組化架構**：設計了 /Source (來源) 及 /Notifier (通知)，方便擴充新的論壇或通知管道。
* **熱重載 (Hot Reload)**：修改 `config.json` 後即時生效，無需重啟程式。
* **智慧去重**：自動記錄已通知過的文章，避免重複干擾。

### 📢 目前支援：PTT (批踢踢實業坊)
* **多看板監控**：同時監控八卦、股票、省錢等多個看板。
* **過濾邏輯**：
    * 支援關鍵字組合 (AND / OR) 與排除 (Exclude)。
    * 支援 **推文數門檻** (例如：只通知 99 推以上的爆文)。
    * 支援 **智慧回溯**：針對高流量看板 (如 Gossiping) 可設定往回掃描 N 頁，不漏失慢熱型文章。
    * 物理排除置底公告文。

## 🗺️ 開發藍圖 (Roadmap / TODO)

### Supported Sources
- [x] **PTT** (v1.0 Completed)
    - [x] 關鍵字/推文數過濾
    - [x] 多頁回溯
    - [x] 排除置底文
- [ ] **Dcard** (Planned)
    - [ ] 熱門文章監控
    - [ ] 指定看板/學校監控
- [ ] **Mobile01** (Future)

### Supported Notifiers
- [x] **Discord** (Webhook)
- [ ] **Line Notify**
- [ ] **Telegram Bot**

## 🛠️ 安裝與執行 (Installation)

### 1. Clone 專案
```bash
git clone [https://github.com/rainstop1205/content-watcher.git](https://github.com/rainstop1205/content-watcher.git)
cd content-watcher
```

### 2. 建立虛擬環境(建議)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

### 3. 安裝依賴套件
```bash
pip install -r requirements.txt
```

### 4. 設定 Config
請將 config.example.json 複製為 config.json 並填入個人化設定：
- webhook_url: 你的 Discord Webhook 網址。
- keywords: 設定你想監控的關鍵字。

### 5. 啟動
```bash
# 直接執行
python main.py
# 或使用背景執行 (Windows)
start.bat
```

## ⚙️ 設定檔範例 (Configuration)
```json
{
  "scan_interval": 30,
  "sources": {
    "ptt": [
      {
        "board_name": "Lifeismoney",
        "keywords": ["1+1", "史低", {"min_push": 20}]
      },
      {
        "board_name": "Gossiping",
        "scan_pages": 5,
        "keywords": [{"min_push": 99, "include": "爆卦"}]
      }
    ],
    "dcard": []
  }
}
```