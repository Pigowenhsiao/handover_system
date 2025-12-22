# Design Notes: 日報フローと紐付け

## Flow
- 起動後にログイン画面を表示し、成功後に「基本情報」画面へ。
- 基本情報（日付/シフト/エリア）未保存の間は他ページと機能ボタンを無効化。
- 基本情報保存後に DailyReport を作成/更新し report_id を保持、他ページを解放。

## Data Linking
- AttendanceEntry / EquipmentLog / LotLog を report_id で DailyReport に紐づけ。
- 出勤保存は upsert：同一 report_id の Regular/Contract を書込/上書き。
- 設備異常/ロット異常は新規レコードとして追加し、履歴は report_id で参照。

## UI
- 画面右上に現在の日報情報（日付/シフト/エリア）を表示。
- 基本情報保存成功時に通知と report_id を表示。
