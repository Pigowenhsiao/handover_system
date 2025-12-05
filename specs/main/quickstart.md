# 快速入門指南 (Quickstart Guide)

## 1. 系統架構概覽 (System Architecture Overview)

電子交接本系統是一個基於 Python 的桌面應用程式，結合了前端界面和後端數據處理。系統採用 SQLite 作為數據庫，支援多語言界面（日文、中文、英文），以單機部署方式運行（資料庫檔與應用程式同機、無需外部 DB 伺服器）。

架構圖:
```
┌─────────────────────────────────────────────────────────────┐
│                    電子交接本系統 (Desktop App)                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   前端界面        │  │   業務邏輯       │  │   數據庫層        │ │
│  │   (Tkinter)     │  │   (Services)    │  │  (SQLite)      │ │
│  │                 │  │                 │  │                 │ │
│  │ - 多語言支持      │  │ - 用戶管理      │  │ - User          │ │
│  │ - 日報表界面      │  │ - 報表管理      │  │ - DailyReport   │ │
│  │ - 出勤記錄界面    │  │ - 出勤管理      │  │ - Attendance    │ │
│  │ - 設備記錄界面    │  │ - 設備管理      │  │ - Equipment     │ │
│  │ - 批次記錄界面    │  │ - 批次管理      │  │ - LotLog        │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 2. 開發環境設置 (Development Environment Setup)

### 2.1 系統要求 (System Requirements)
- **作業系統**: Windows 7+, macOS 10.12+, 或 Linux 發行版
- **Python 版本**: 3.9 或更高版本
- **記憶體**: 最少 2GB RAM
- **硬碟空間**: 最少 100MB 可用空間
- **資料庫**: 無需外部資料庫服務，使用本機 SQLite 檔案

### 2.2 依賴套件 (Dependencies)
系統需要以下 Python 套件:
```
python >= 3.9
sqlite3 (Python 內建)
tkinter (Python 內建)
fastapi
sqlalchemy
bcrypt
pillow
python-multipart
python-jose[cryptography]
i18n
```

安裝命令:
```bash
pip install fastapi sqlalchemy bcrypt pillow python-multipart python-jose[cryptography] i18n
```

### 2.3 專案結構 (Project Structure)
```
handover_system/
├── backend/
│   ├── main.py                 # 應用程式入口點
│   ├── database/
│   │   ├── base.py             # 資料庫連接和會話管理
│   │   ├── init_db.py          # 資料庫初始化
│   │   └── models/             # 數據模型
│   ├── api/
│   │   ├── deps.py             # 依賴注入函數
│   │   ├── auth.py             # 認證端點
│   │   └── routes/             # API 路由定義
│   ├── schemas/                # Pydantic 模型 (API 驗證)
│   ├── services/               # 業務邏輯服務
│   ├── utils/                  # 工具函數
│   └── config/                 # 配置設定
├── frontend/
│   ├── public/
│   │   ├── index.html          # 主 HTML 入口點
│   │   └── locales/            # 翻譯文件 (zh.json, ja.json, en.json)
│   └── src/
│       ├── components/         # 可重複使用的 UI 組件
│       └── services/           # 服務 API 呼叫
├── uploads/                    # 上傳文件存儲 (設備圖片)
├── docs/                       # 文件
└── tests/                      # 測試文件
```

## 3. 主要功能模組 (Core Feature Modules)

### 3.1 用戶管理 (User Management)
- 登入/登出功能
- 使用者角色管理 (管理員/一般使用者)
- 密碼安全 (使用 bcrypt 加密)

### 3.2 日報表 (Daily Reporting)
- 每日工作摘要 (Key Output, Issues, Countermeasures)
- 日期和班別選擇
- 區域選擇

### 3.3 出勤管理 (Attendance Management)
- 正社員和契約社員同時記錄
- 定員、出勤、欠勤、理由記錄
- 同時顯示兩種職類別的輸入欄位

### 3.4 設備管理 (Equipment Management)
- 設備異常記錄
- 發生時刻、影響數量、對應內容
- 圖片上傳功能

### 3.5 批次管理 (Lot Management)
- 異常批次記錄
- 批號、異常內容、處置狀況、特記事項

## 4. API 端點 (API Endpoints)

### 4.1 認證端點 (Authentication Endpoints)
- `POST /api/auth/login` - 使用者登入
- `POST /api/auth/logout` - 使用者登出

### 4.2 報表端點 (Report Endpoints)
- `GET /api/reports` - 獲取報表列表
- `POST /api/reports` - 創建新報表
- `PUT /api/reports/{id}` - 更新報表
- `DELETE /api/reports/{id}` - 刪除報表

### 4.3 出勤端點 (Attendance Endpoints)
- `GET /api/attendance/{report_id}` - 獲取出勤記錄
- `POST /api/attendance` - 添加出勤記錄
- `PUT /api/attendance/{id}` - 更新出勤記錄
- `DELETE /api/attendance/{id}` - 刪除出勤記錄

### 4.4 多語言端點 (Multilingual Endpoints)
- `GET /api/languages/resources` - 獲取語言資源
- `PUT /api/languages/settings` - 更新語言設置

## 5. 開始運行 (Getting Started)

### 5.1 首次運行 (First Run)
1. 克隆或下載專案到本地目錄
2. 安裝所需的依賴套件
3. 初始化數據庫:
   ```bash
   python backend/database/init_db.py
   ```
4. 運行應用程式:
   ```bash
   python backend/main.py
   ```
5. 系統將在本機自動創建 SQLite 數據庫檔和默認管理員帳戶

### 5.2 默認管理員帳戶 (Default Admin Account)
- **用戶名**: `admin`
- **密碼**: `1234` (首次運行後應立即更改)

## 6. 開發指南 (Development Guide)

### 6.1 添加新功能 (Adding New Features)
1. 在對應的 models 中定義數據結構
2. 在 schemas 中定義 API 驗證模型
3. 在 services 中實現業務邏輯
4. 在 api/routes 中添加路由
5. 在前端界面中添加對應的功能組件

### 6.2 多語言支援 (Multi-language Support)
1. 在 `frontend/public/locales/` 中添加對應語言的 JSON 文件
2. 使用 `i18n` 函數在界面中獲取翻譯文本
3. 驗證文本在所有支持語言中都有正確翻譯

### 6.3 數據庫遷移 (Database Migration)
- 使用 SQLAlchemy Alembic 進行數據庫遷移管理
- 為每個重大更新創建遷移腳本
- 測試遷移腳本在不同環境中的運行

## 7. 部署 (Deployment)

### 7.1 桌面應用部署 (Desktop App Deployment)
1. 使用 PyInstaller 打包應用程式:
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --add-data "frontend;frontend" --add-data "uploads;uploads" backend/main.py
```

2. 將生成的可執行文件分發給用戶

### 7.2 配置管理 (Configuration Management)
- 所有配置保存在 `config/settings.py` 中
- 支援環境變量覆蓋默認設定
- 敏感配置（如密鑰）應從環境變量加載

8. 測試 (Testing)

### 8.1 單元測試 (Unit Tests)
運行單元測試:
```bash
python -m pytest tests/unit/
```

### 8.2 整合測試 (Integration Tests)
運行整合測試:
```bash
python -m pytest tests/integration/
```

### 8.3 測試覆蓋率 (Test Coverage)
確保測試覆蓋率達到 80% 以上:
```bash
python -m pytest --cov=backend --cov-report=html
```
