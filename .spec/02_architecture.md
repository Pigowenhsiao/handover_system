# 技術架構與資料庫設計 (Technical Plan)

## 1. 技術堆疊 (Tech Stack)
- **語言**: Python 3.9+
- **前端框架**: Streamlit（單機本機 UI，不需額外後端服務或 API）
- **資料庫**: SQLite（檔案型，離線可用）
- **ORM**: SQLAlchemy（禁止 Raw SQL，避免注入風險）
- **認證**: Session State + Bcrypt（或 Streamlit-Authenticator），不使用 JWT（單機無 API 需求）

## 2. 資料庫 Schema (SQLAlchemy Models)

### User Table
- id (PK)
- username (String, Unique)
- password_hash (String)
- role (String: 'admin', 'user')

### DailyReport Table (主表)
- id (PK)
- date (Date)
- shift (String)
- area (String)
- author_id (FK -> User.id)
- created_at (DateTime)
- summary_key_output (Text)
- summary_issues (Text)
- summary_countermeasures (Text)

### AttendanceEntry Table
- id (PK)
- report_id (FK -> DailyReport.id)
- category (String: 'Regular', 'Contract')
- scheduled_count (Int)
- present_count (Int)
- absent_count (Int)
- reason (Text)

### EquipmentLog Table
- id (PK)
- report_id (FK -> DailyReport.id)
- equip_id (String)
- description (Text)
- start_time (String)
- impact_qty (Int)
- action_taken (Text)
- image_path (String, Optional)

### LotLog Table
- id (PK)
- report_id (FK -> DailyReport.id)
- lot_id (String)
- description (Text)
- status (Text)
- notes (Text)

## 3. UI/UX 規劃
- **側邊欄導航**：登入者資訊、填寫日報、歷史查詢、登出。
- **填寫頁面 (Entry Page)**:
  - 使用 `st.form` 包裹提交按鈕。
  - 使用 `st.data_editor` 處理「出勤」、「設備異常」、「異常批次」多筆輸入。
  - 圖片上傳功能，儲存至 `uploads/` 資料夾並記錄路徑
- **查詢頁面**：提供日期、區域篩選，顯示歷史報表清單
- **語系**：UI 文字使用繁體中文；多語切換需求可由翻譯資源表支援。
