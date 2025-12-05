# Project Context

## Purpose
單機版電子交接本與多語言管理系統，取代紙本/ PDF 日報表。提供桌面 GUI（tkinter）讓管理員維護翻譯資源、切換日/中/英介面，並支援登入、出勤、設備異常、異常批次、總結與照片上傳等交接/報表功能。目標是離線可用、安裝即用，降低部署與運維成本。

## Tech Stack
- 語言：Python 3.9+
- 前端框架：Streamlit（快速構建資料輸入與報表 App）
- 資料庫：SQLite（檔案型，易部署）
- ORM：SQLAlchemy
- 認證：Streamlit-Authenticator 或 Session State + Bcrypt
- 測試/驗證：內建驗證腳本 `verify_features.py`、`verify_implementation.py`

## Project Conventions

### Code Style
- 以標準 Python 風格為主，遵守 PEP8；必要時加入簡潔註解說明非直覺邏輯。
- 優先使用內建模組與標準庫；避免不必要的第三方依賴。

### Architecture Patterns
- 單機 Web/桌面混合應用：以 Streamlit 提供介面，後端與資料庫均在本機執行。
- 分層：介面層（Streamlit UI）、應用層（業務邏輯/Session State）、資料層（SQLAlchemy + SQLite）。
- 認證：Session State 管理登入狀態，可搭配 Streamlit-Authenticator 或自行實作 Bcrypt 雜湊驗證。

### Testing Strategy
- 以輕量驗證腳本為主：`verify_features.py`、`verify_implementation.py`。
- 手動功能檢查重點：多語切換、翻譯 CRUD、匯入 JSON、交接/出勤相關界面。
- 無外部 CI；本機執行 Python 腳本與手動走查為主。

### Git Workflow
- 預設主幹開發；如需分支以功能命名（kebab-case），完成後合併回主分支。
- 提交訊息簡潔描述變更與影響，例如 `fix-lang-import-null`、`add-attendance-ui`.

## Domain Context
- 目標使用者：管理員與一般員工；管理員可維護翻譯與交接資料。
- 離線運行：不依賴網路或遠端服務，資料保存在本機 SQLite。
- 多語言資源可透過 GUI 匯入/修改，立即反映於介面。

## Functional Requirements 摘要
- 使用者故事：登入後填寫交接日報；可切換日/夜班與區域（etching_D、etching_E、litho、thin_film）；可新增多筆設備異常與異常批次；填寫 Key Machine Output / Key Issues / Countermeasures 總結；可上傳照片；管理者可查詢日期範圍並匯出。
- 基礎資訊：日期 YYYY/MM/DD；班別下拉 [Day, Night]；區域下拉 [etching_D, etching_E, litho, thin_film]；填寫者帶入登入者。
- 出勤：記錄正社員、契約/派遣的定員、出勤、欠勤、理由。
- 設備異常：每筆含設備番号、異常內容、發生時刻、影響數量、對應內容，可動態多筆。
- 本日異常批次：每筆含異常內容、處置狀況、特記事項，可動態多筆。
- 總結：Key Machine Output、Key Issues、Countermeasures（文字欄位）。

## Data Model (SQLAlchemy Models)
- User：`id`、`username`（唯一）、`password_hash`、`role`（admin/user）。
- DailyReport：`id`、`date`、`shift`、`area`、`author_id`、`created_at`、`summary_key_output`、`summary_issues`、`summary_countermeasures`。
- AttendanceEntry：`id`、`report_id`、`category`（Regular/Contract）、`scheduled_count`、`present_count`、`absent_count`、`reason`。
- EquipmentLog：`id`、`report_id`、`equip_id`、`description`、`start_time`、`impact_qty`、`action_taken`、`image_path`（可選）。
- LotLog：`id`、`report_id`、`lot_id`、`description`、`status`、`notes`。

## UI/UX 佈局
- 側邊欄：登入者資訊、功能導航（填寫日報、歷史查詢、登出）。
- 填寫頁面：使用 `st.form` 包裹提交；`st.data_editor` 處理設備異常與異常批次的動態表格；`st.file_uploader` 上傳圖片到 `uploads/`，並記錄路徑。

## Important Constraints
- 不使用網路存取或雲端服務，所有資源需本機可用。
- 維持 Python 3.9+ 相容；避免需要編譯或平台特定依賴。
- 介面與資料庫檔案須放在同一目錄以確保可移植性。

## External Dependencies
- 無外部 API 或服務；僅依賴 Python 標準庫與本機 SQLite。
