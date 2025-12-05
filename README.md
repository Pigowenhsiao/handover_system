# 電子交接本系統使用說明

## 概述
單機 Streamlit 應用，Python 3.9+ 與本機 SQLite。支援登入、日報填寫（出勤、設備異常、異常批次、總結、照片上傳）、日期/區域查詢與匯出。介面文字為繁體中文，透過 Sidebar 導航。

## 系統需求
- Python 3.9+
- 依賴套件：`streamlit`, `sqlalchemy`, `pandas`, `bcrypt`（詳見 `requirements.txt`）
- 可讀寫本機 SQLite 檔案（無需遠端服務）

## 快速開始
1) 安裝 Python 3.9+  
2) `pip install -r requirements.txt`  
3) 執行 `streamlit run app.py`  
4) 首次啟動會自動建立資料庫與預設管理員帳號（請立即修改密碼）

## 功能說明
- 登入/登出：Session State 管理。
- 日報填寫：PDF 對應欄位，班別/區域下拉；出勤、設備異常、異常批次使用 `st.data_editor` 動態多筆；支援圖片上傳至 `uploads/`。
- 總結：Key Machine Output / Key Issues / Countermeasures。
- 歷史查詢：依日期與區域篩選列表，可匯出 CSV。
- 使用者管理（管理員）：新增/刪除/修改使用者。
- 修改密碼：使用者可自行更新密碼（需輸入舊密碼）。

## 數據庫
- 本機 SQLite 檔案，模型定義於 `models.py`。
- 主要表格：User、DailyReport、AttendanceEntry、EquipmentLog、LotLog。

## 技術架構
- UI：Streamlit（Sidebar 導航），介面文字為繁體中文。
- 應用層：Session State 管控登入狀態，業務邏輯分散於 `views/`。
- 資料層：SQLAlchemy ORM 對 SQLite，禁止 Raw SQL。

## 注意事項
1. 確保 `uploads/` 可寫入以儲存圖片。
2. 不需網路與後端 API，所有邏輯本機執行。
3. 密碼以 bcrypt 雜湊存放，請妥善保管管理員密碼。

## 組織結構
- `app.py`: Streamlit 入口與側邊欄導航
- `models.py`: SQLAlchemy 模型與 `init_db`
- `auth.py`: 密碼雜湊與驗證
- `views/`: 界面模組（例如 `daily_entry.py`, `report_view.py`）
- `uploads/`: 圖片上傳儲存位置

## 疑難排解
1. 確認已安裝依賴 `pip install -r requirements.txt`
2. 若啟動失敗，請查看終端錯誤訊息
3. 確認 `app.py`、`models.py`、`auth.py` 存在且可讀
4. 確認目前使用者對資料庫檔與 `uploads/` 有讀寫權限
