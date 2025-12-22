# 内部インターフェース規約 (Main Spec Contracts)

本システムは単機デスクトップアプリであり、REST API は提供しません。以下は内部インターフェース規約の要約です。

## 1. 日報と関連データ
- upsert_daily_report(date, shift, area, author_id, summary_fields) -> report_id
- get_daily_report(date, shift, area) -> DailyReport | None
- save_attendance(report_id, regular_data, contract_data) -> bool
- list_equipment_logs(report_id) -> list
- list_lot_logs(report_id) -> list

## 2. 統計と履歴
- build_attendance_summary(start_date, end_date, shift?, area?) -> table + chart_data
- search_abnormal_history(start_date, end_date, shift?, area?) -> equipment_logs + lot_logs

## 3. 設定
- load_settings() -> {auto_backup, backup_interval_days}
- save_settings(auto_backup, backup_interval_days) -> bool

## 4. 将来拡張
将来 REST API などのサービス化を行う場合は、別途 API 契約書を追加し、エンドポイント/認可/入出力仕様を明記すること。
