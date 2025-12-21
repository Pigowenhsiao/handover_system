# Main Spec Implementation Plan (現況)

本專案為單機桌面應用，以下為現行結構與技術背景，提供後續維護參考。

## 技術背景
- Language/Version: Python 3.9+
- GUI: Tkinter/ttk
- DB: SQLite（本機）
- ORM: SQLAlchemy
- Auth: bcrypt
- Chart: matplotlib（嵌入 Tkinter）

## 專案結構（實際）
```
handover_system/
├── run_modern_system.py          # 現代化介面啟動器
├── app.py                        # 舊版介面入口（已停止更新）
├── models.py                     # SQLAlchemy models
├── auth.py                       # 密碼雜湊/驗證
├── frontend/
│   ├── main.py                   # 語言管理與 UI 啟動
│   └── src/
│       └── components/           # Tkinter UI 元件
├── frontend/public/locales/      # 多語資源
├── handover_system.db            # SQLite 資料庫（執行後產生）
└── handover_settings.json        # 系統設定（執行後產生）
```

## 現況里程碑
- 多語言切換（中/英/日）已完成
- 日報流程、出勤、設備異常、批次異常已完成
- 總結頁改為出勤統計（表格 + 圖表）已完成
- 異常歷史查詢（雙表格 + 篩選）已完成
- 管理功能（使用者/翻譯/班別/區域）已完成
