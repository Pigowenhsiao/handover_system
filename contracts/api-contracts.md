# 內部介面約定 (Interface Contracts)

本系統為單機桌面應用，無 REST API。以下為 UI 與資料層的內部介面約定與資料流說明。

## 1. 資料存取介面 (Data Access)

### 1.1 使用者管理
- create_user(username, password, role) -> bool
- authenticate_user(username, password) -> User | None
- update_user(user_id, username?, password?, role?) -> bool
- delete_user(user_id) -> bool

### 1.2 日報表
- upsert_daily_report(date, shift, area, author_id, summary_fields) -> report_id
- get_daily_report(date, shift, area) -> DailyReport | None

### 1.3 出勤記錄
- save_attendance(report_id, regular_data, contract_data) -> bool
- get_attendance(report_id) -> list

### 1.4 設備異常 / 異常批次
- add_equipment_log(report_id, payload) -> bool
- add_lot_log(report_id, payload) -> bool
- list_equipment_logs(report_id) -> list
- list_lot_logs(report_id) -> list

### 1.5 Delay List / Summary Actual
- import_delay_list(rows) -> temp_cache
- upload_delay_list(rows) -> bool
- import_summary_actual(rows) -> temp_cache
- upload_summary_actual(rows) -> bool

### 1.6 統計與查詢
- build_attendance_summary(start_date, end_date, shift?, area?) -> table + chart_data
- search_abnormal_history(start_date, end_date, shift?, area?) -> equipment_logs + lot_logs

### 1.7 設定
- load_settings() -> {auto_backup, backup_interval_days}
- save_settings(auto_backup, backup_interval_days) -> bool

## 2. UI 互動約定 (UI Flow)

- 登入成功後才顯示功能頁面。
- 基本資訊 (日期/班別/區域) 儲存成功後，其他功能頁面解鎖。
- 右上角顯示當前日報表資訊，作為各頁資料關聯基準。

## 3. 錯誤處理

- 所有輸入需驗證並提示錯誤訊息。
- 寫入失敗需顯示錯誤並保持原資料不被覆蓋。
- 缺少翻譯鍵應回退預設文字。
