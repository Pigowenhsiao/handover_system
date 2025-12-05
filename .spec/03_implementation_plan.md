# 開發任務清單 (Tasks)

請依序執行以下步驟來構建應用程式：

## Phase 1: 基礎設施
1. [ ] 建立 `requirements.txt`: 包含 streamlit, sqlalchemy, pandas, bcrypt。
2. [ ] 建立 `models.py`: 根據 `02_architecture.md` 實作 SQLAlchemy Classes 和 `init_db` 函數。
3. [ ] 建立 `auth.py`: 實作密碼雜湊與驗證邏輯。

## Phase 2: 核心功能
4. [ ] 建立 `app.py`: 設定 Streamlit 頁面配置、Session State 管理與側邊欄導航。
5. [ ] 建立 `views/daily_entry.py`:
    - 實作 PDF 對應的輸入介面。
    - 使用 `st.data_editor` 實作多行輸入。
    - 實作資料儲存邏輯 (寫入 SQLite)。
6. [ ] 建立 `views/report_view.py`:
    - 實作依照日期與區域篩選。
    - 顯示歷史報表清單。

## Phase 3: 優化與測試
7. [ ] 添加圖片上傳處理邏輯 (儲存檔案到本機)。
8. [ ] 測試使用者登入與資料寫入流程。
