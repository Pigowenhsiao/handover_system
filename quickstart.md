# 快速入門指南 (Quickstart Guide)

## 1. 系統概述 (System Overview)

電子交接本系統是一個支援多語言的桌面應用程式，用於記錄和管理生產線的日常交接。支援日文/中文/英文，涵蓋使用者管理、設備異常、批次追蹤、出勤記錄；單機部署，資料庫為本機 SQLite，無需伺服器。

## 2. 開發環境設置 (Development Environment Setup)

### 2.1 系統要求
- **作業系統**: Windows 10+, macOS 10.14+, 或 Linux 發行版
- **Python 版本**: 3.9 或更高版本
- **記憶體**: 最少 2GB RAM
- **硬碟空間**: 最少 100MB 可用空間
- **資料庫**: 無需外部 DB 伺服器，使用本機 SQLite 檔案

### 2.2 依賴套件 (Dependencies)
系統需要以下 Python 套件（內建的 sqlite3、tkinter 無需另裝）:
- python >= 3.9
- sqlite3 (Python 內建)
- tkinter (Python 內建)
- pillow >= 8.0.0 (用於圖片處理)
- bcrypt >= 4.0.0 (用於密碼加密)

安裝命令:
```bash
pip install pillow bcrypt
```

### 2.3 專案結構 (Project Structure)
```
handover_system/
├── main.py                 # 主入口點
├── handover_app.py         # 應用程式主類
├── language_manager.py     # 語言管理
├── database_manager.py     # 數據庫管理
├── models/                 # 數據模型
│   ├── user.py            # 用戶模型
│   ├── daily_report.py    # 日報表模型
│   ├── attendance.py      # 出勤記錄模型
│   └── equipment.py       # 設備記錄模型
├── api/                    # API 接口
├── specs/                  # 規格文件
├── uploads/                # 上傳文件存儲
├── configs/                # 配置文件
└── README.md               # 說明文件
```

## 3. 開始使用 (Getting Started)

### 3.1 首次運行 (First Run)
1. 克隆或下載專案到本地
2. 安裝依賴
3. 執行 `python main.py`（或 Windows 雙擊 `start.bat`）
4. 系統會在本機建立 SQLite 資料庫並建立初始管理員 (admin/1234)

### 3.2 系統初始化 (System Initialization)
首次啟動自動完成：
- 本機建立 SQLite 數據庫檔
- 建立所有必要的資料表
- 添加預設管理員帳戶
- 載入初始語言資源

## 4. 主要功能使用 (Main Features Usage)

### 4.1 登入系統 (Login to System)
1. 啟動應用程式
2. 輸入帳密；預設管理員：`admin` / `1234`

### 4.2 語言切換 (Language Switching)
- 使用頂部工具欄的語言選擇器
- 支援日文、中文、英文三種語言
- 界面標示會即時更新

### 4.3 填寫日報表 (Filling Daily Reports)
1. 點擊「填寫日報」
2. 填入日期、班別、區域
3. 填寫 Key Output / Issues / Countermeasures
4. 填寫出勤、設備異常、異常批次
5. 按「保存」

### 4.4 管理使用者 (User Management)
1. 以管理員登入
2. 點擊「使用者管理」
3. 在新視窗中新增/修改/刪除帳戶
4. 按「保存」或「取消」

## 5. 開發指南 (Development Guide)

### 5.1 添加新功能 (Adding New Features)
1. 參考 `specs/` 目錄中的規格文件
2. 在對應的模型中添加數據結構
3. 在界面中添加相關組件
4. 連接數據邏輯和界面組件
5. 測試新功能

### 5.2 多語言支援 (Multi-language Support)
1. 在對應的語言資源文件中添加翻譯
   - 日文: `locale/ja.json`
   - 中文: `locale/zh.json`
   - 英文: `locale/en.json`
2. 使用 `language_manager` 的 `translate()` 方法獲取翻譯文本

### 5.3 數據模型擴展 (Extending Data Models)
- 所有數據模型都繼承自基礎模型類
- 使用 SQLAlchemy ORM 定義數據結構
- 在模型中定義驗證邏輯
- 使用遷移腳本更新數據庫結構

## 6. API 接口 (API Interfaces)

系統為桌面應用，無對外 REST API；以下為內部介面：

### 6.1 資料庫接口 (Database Interface)
- `create_user(username, password, role)`: 創建用戶
- `authenticate_user(username, password)`: 驗證用戶
- `create_daily_report(...)`: 創建日報表
- `add_attendance_entry(...)`: 添加出勤記錄
- `add_equipment_log(...)`: 添加設備異常記錄

### 6.2 界面接口 (UI Interface)
- `change_language(lang_code)`: 切換語言
- `update_display_texts()`: 更新顯示文本
- `refresh_data_grid()`: 重新整理數據網格

## 7. 錯誤處理 (Error Handling)

### 7.1 常見錯誤 (Common Errors)
- **數據庫連接錯誤**: 檢查數據庫文件路徑和權限
- **語言資源加載失敗**: 檢查語言資源文件是否存在
- **用戶驗證失敗**: 檢查用戶名和密碼是否正確

### 7.2 調試技巧 (Debugging Tips)
- 在開發模式下運行以獲得詳細日誌
- 檢查 `logs/` 目錄中的日誌文件
- 使用 Python 調試器進行逐步調試

## 8. 部署 (Deployment)

### 8.1 桌面應用部署 (Desktop App Deployment)
1. 使用 PyInstaller 打包：
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --add-data "locale;locale" main.py
```
2. 分發可執行檔
3. 確保目標機可讀寫本機 SQLite 檔（無需部署 DB 伺服器）

### 8.2 配置文件 (Configuration Files)
所有配置保存在 `configs/` 目錄中:
- `app_settings.json`: 應用程式基本設定
- `db_config.ini`: 數據庫連接設定
- `ui_settings.json`: 用戶界面設定

## 9. 維護與支援 (Maintenance and Support)

### 9.1 數據備份 (Data Backup)
定期備份 `handover_system.db`（建議每日一次），確保數據安全。

### 9.2 更新系統 (Updating the System)
1. 備份資料庫與配置
2. 更新應用檔案
3. 如需，執行資料庫遷移腳本
4. 驗證主要功能

## 10. 安全性注意事項 (Security Considerations)

- 密碼使用 bcrypt 加密存儲
- 提供安全的用戶權限管理
- 防止 SQL 注入和其他常見漏洞
- 定期更新依賴套件以修補安全漏洞
