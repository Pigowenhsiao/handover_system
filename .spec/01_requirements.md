# 專案需求規格書: 電子交接本系統 (Handover System)

## 1. 專案概述
開發一個基於 Python 的電子交接本系統，用於取代紙本 (PDF) 日報表。系統需支援人員登入、資料庫存儲、報表查詢及圖片上傳功能。

## 2. 核心使用者故事 (User Stories)
- **作為使用者**，我需要透過帳號密碼登入，以確保資料歸屬正確。
- **作為使用者**，我需要填寫「出勤」、「設備異常」、「異常批次」和「總結」，並能上傳照片。
- **作為使用者**，我需要在填寫時使用下拉選單選擇「班別」和「區域」，以減少輸入錯誤。
- **作為管理者**，我需要能查詢特定日期範圍的報表，並匯出資料。
- **作為系統管理員**，我需要一個維護介面來管理使用者帳號（新增、刪除、修改）。

## 3. 詳細欄位定義 (基於 25.11.24E_etching_Daily_Report.pdf)

### 3.1 基礎資訊 (Header)
- **日期 (Date)**: YYYY/MM/DD
- **班別 (Shift)**: 下拉選單 [Day, Night]
- **區域 (Area)**: 下拉選單 [etching_D, etching_E, litho, thin_film]
- **填寫者 (Author)**: 自動帶入登入者名稱

### 3.2 出勤狀況 (Attendance Status)
需記錄以下類別的 `定員(Scheduled)`, `出勤(Present)`, `欠勤(Absent)`, `理由(Reason)`:
1. 正社員 (Regular Employee)
2. 契約社員・派遣社員 (Contract/Temp Staff)

### 3.3 設備異常 (Equipment Abnormalities)
可動態新增多筆資料，每筆包含：
- 設備番号 (Equipment ID)
- 異常內容 (Description)
- 發生時刻 (Start Time)
- 影響數量 (Affected Quantity)
- 對應內容 (Action Taken)

### 3.4 本日異常批次 (Abnormal Lots)
可動態新增多筆資料，每筆包含：
- 批號 (Lot ID)
- 異常內容 (Description)
- 處置狀況 (Handling Status)
- 特記事項 (Special Notes)

### 3.5 總結 (Summary)
- Key Machine Output (文字)
- Key Issues (文字)
- Countermeasures (文字)

## 4. 系統管理功能
- **使用者管理**：管理員可以新增、刪除和修改使用者帳號資訊，包括使用者名稱、角色和密碼。

## 5. 技術架構澄清（單機 Streamlit）
- UI：使用 Streamlit，透過 Sidebar 導航，所有介面文字使用繁體中文。
- 資料庫：本機 SQLite，透過 SQLAlchemy 操作，禁止 Raw SQL。
- 認證：Session State + Bcrypt（或 Streamlit-Authenticator），不使用 JWT（單機不需 API）。
- 架構：單機執行，不需後端 API；與 PDF 邏輯結構對齊，出勤/設備異常/異常批次使用 `st.data_editor`。

## 6. 已澄清問題
### 2025-11-25 會議決議（更新）
- **Q**: 技術架構採用哪種方案？
  - **A**: 採用單機 Streamlit + SQLite（無 Flask/FastAPI，無前後端分離）。
- **Q**: 是否需要使用者管理介面？
  - **A**: 是，系統管理員需要一個維護介面來管理使用者帳號（新增、刪除、修改）。
- **Q**: 使用者認證方式？
  - **A**: 採用 Session State + Bcrypt（或 Streamlit-Authenticator），不使用 JWT。
