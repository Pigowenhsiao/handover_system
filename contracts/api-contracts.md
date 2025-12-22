# 内部インターフェース規約 (Interface Contracts)

本システムは単機デスクトップアプリであり、REST API は提供しません。以下は UI とデータ層の内部インターフェース規約およびデータフローの説明です。

## 1. データアクセス (Data Access)

### 1.1 ユーザー管理
- create_user(username, password, role) -> bool
- authenticate_user(username, password) -> User | None
- update_user(user_id, username?, password?, role?) -> bool
- delete_user(user_id) -> bool

### 1.2 日報
- upsert_daily_report(date, shift, area, author_id, summary_fields) -> report_id
- get_daily_report(date, shift, area) -> DailyReport | None

### 1.3 出勤記録
- save_attendance(report_id, regular_data, contract_data) -> bool
- get_attendance(report_id) -> list

### 1.4 設備異常 / 異常ロット
- add_equipment_log(report_id, payload) -> bool
- add_lot_log(report_id, payload) -> bool
- list_equipment_logs(report_id) -> list
- list_lot_logs(report_id) -> list

### 1.5 Delay List / Summary Actual
- import_delay_list(rows) -> temp_cache
- upload_delay_list(rows) -> bool
- import_summary_actual(rows) -> temp_cache
- upload_summary_actual(rows) -> bool

### 1.6 統計・照会
- build_attendance_summary(start_date, end_date, shift?, area?) -> table + chart_data
- search_abnormal_history(start_date, end_date, shift?, area?) -> equipment_logs + lot_logs

### 1.7 設定
- load_settings() -> {auto_backup, backup_interval_days}
- save_settings(auto_backup, backup_interval_days) -> bool

## 2. UI フロー (UI Flow)

- ログイン成功後に機能ページを表示。
- 基本情報（日付/シフト/エリア）保存後に他の機能ページが解放。
- 右上に現在の日報情報を表示し、各ページの関連付けの基準とする。

## 3. エラー処理

- 全入力を検証し、エラーメッセージを表示。
- 書き込み失敗時はエラー表示し、既存データを保持。
- 翻訳キーが欠落している場合は既定文言にフォールバック。
