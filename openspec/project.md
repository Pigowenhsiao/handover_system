# Project Context

## Purpose
單機版電子交接本與多語言管理系統，取代紙本/ PDF 日報表。提供桌面 GUI（tkinter）讓管理員維護翻譯資源、切換日/中/英介面，並支援登入、出勤、設備異常、異常批次、總結與照片上傳等交接/報表功能。目標是離線可用、安裝即用，降低部署與運維成本。

## Tech Stack
- 語言：Python 3.9+
- GUI：Tkinter / ttk（桌面應用，支援可調整大小與分頁）
- 資料庫：SQLite（檔案型，易部署）
- ORM：SQLAlchemy
- 認證：bcrypt（本機密碼雜湊）
- 資料處理：pandas、openpyxl（Excel 匯入）
- 圖表：matplotlib（嵌入 Tkinter 顯示）
- 測試/驗證：`verify_features.py`、`verify_implementation.py`，以及 `tests/` 內的腳本

## Project Conventions

### Code Style
- 以標準 Python 風格為主，遵守 PEP8；必要時加入簡潔註解說明非直覺邏輯。
- 優先使用內建模組與標準庫；避免不必要的第三方依賴。

### Entry Point
- 現代化介面啟動入口為 `run_modern_system.py`（建議使用）。

### Architecture Patterns
- 單機桌面應用：Tkinter GUI 與資料庫均在本機執行。
- 分層：介面層（Tkinter UI）、應用層（業務邏輯/資料驗證）、資料層（SQLAlchemy + SQLite）。
- 認證：本機資料庫儲存密碼雜湊（bcrypt），登入狀態由 GUI 狀態管理。

### Testing Strategy
- 以輕量驗證腳本為主：`verify_features.py`、`verify_implementation.py`。
- 自動化測試以 `tests/` 的腳本為主（含 UI/效能/安全/整合）。
- 手動功能檢查重點：多語切換、日報/報表流程、Excel 匯入與上傳、管理功能。
- 無外部 CI；本機執行 Python 腳本與手動走查為主。

### Git Workflow
- 預設主幹開發；如需分支以功能命名（kebab-case），完成後合併回主分支。
- 提交訊息簡潔描述變更與影響，例如 `fix-lang-import-null`、`add-attendance-ui`.

## Domain Context
- 目標使用者：管理員與一般員工；管理員可維護翻譯與交接資料。
- 離線運行：不依賴網路或遠端服務，資料保存在本機 SQLite。
- 多語言資源可透過 GUI 匯入/修改，立即反映於介面。

## Functional Requirements 摘要
- 使用者故事：登入後先儲存日報基本資訊（日期/班別/區域）才能使用其他功能。
- 日報唯一性：同日期 + 班別 + 區域視為同一筆日報，儲存時會覆寫舊資料。
- 基礎資訊：日期採日曆選擇器；班別下拉 [Day, Night]；區域下拉 [etching_D, etching_E, litho, thin_film]；填寫者帶入登入者。
- 出勤：記錄正職/契約的定員、出勤、欠勤、理由。
- 設備異常：每筆含設備號碼、異常內容、發生時刻、影響數量、對應內容，可動態多筆。
- 異常批次：每筆含批號、異常內容、處置狀況、特記事項，可動態多筆。
- 總結：改為出勤統計（表格 + 出勤率折線圖 + 出勤人數堆疊柱狀圖），日期區間預設當月 1 號到今天。
- 異常歷史：設備異常與異常批次歷史查詢（雙表格），支援日期區間與班別/區域篩選。
- 報表匯入：Delay List 與 Summary Actual 支援 Excel 匯入 → 暫存 → 上傳流程。

## Data Model (SQLAlchemy Models)
- User：`id`、`username`（唯一）、`password_hash`、`role`（admin/user）。
- ShiftOption：`id`、`name`（Day/Night 等）。
- AreaOption：`id`、`name`（etching_D、etching_E、litho、thin_film 等）。
- DailyReport：`id`、`date`、`shift`、`area`、`author_id`、`created_at`、`summary_key_output`、`summary_issues`、`summary_countermeasures`。
- AttendanceEntry：`id`、`report_id`、`category`（Regular/Contract）、`scheduled_count`、`present_count`、`absent_count`、`reason`。
- EquipmentLog：`id`、`report_id`、`equip_id`、`description`、`start_time`、`impact_qty`、`action_taken`、`image_path`（可選）。
- LotLog：`id`、`report_id`、`lot_id`、`description`、`status`、`notes`。
- DelayEntry：`id`、`delay_date`、`time_range`、`reactor`、`process`、`lot`、`wafer`、`progress`、`prev_steps`、`prev_time`、`severity`、`action`、`note`。
- SummaryActualEntry：`id`、`summary_date`、`label`、`plan`、`completed`、`in_process`、`on_track`、`at_risk`、`delayed`、`no_data`、`scrapped`。

## UI/UX 佈局
- 登入視窗：登入後進入主視窗（支援多語切換）。
- 主視窗：左側導覽選單 + 右側內容區（卡片式佈局）。
- 資料表格：`ttk.Treeview` 呈現查詢/彙總，雙擊列進入編輯視窗。
- 檔案匯入/上傳：`filedialog` 選擇 Excel/圖片，寫入本機檔案或 SQLite。
- 圖表：matplotlib 嵌入 Tkinter 顯示。

## Important Constraints
- 不使用網路存取或雲端服務，所有資源需本機可用。
- 維持 Python 3.9+ 相容；避免需要編譯或平台特定依賴。
- 介面與資料庫檔案需放在同一專案根目錄下，資料庫存放於 `data/handover_system.db` 以確保可移植性。

## External Dependencies
- 無外部 API 或服務；依賴本機套件：SQLAlchemy、pandas、openpyxl、matplotlib、bcrypt（Tkinter 為 Python 內建）。

