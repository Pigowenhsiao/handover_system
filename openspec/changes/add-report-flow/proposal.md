# Change: ログイン + 基本情報ゲート + 日報紐付け

## Why
現行のモダン UI は未ログイン/未設定でも操作でき、出勤/設備/ロットが日報に紐づかず、追跡性と一貫性が不足している。

## What Changes
- 単一ログイン画面を追加し、ログイン前は主機能に入れない。
- 基本情報（日時/シフト/エリア）保存ゲートを追加。
- 基本情報保存時に DailyReport を作成/更新し、サマリー欄を保存。
- 出勤/設備異常/異常ロットの追加と保存を DailyReport に紐づける（report_id）。
- 右上に現在の日報情報（日時/シフト/エリア）を表示。

## Impact
- Affected specs: report-flow (new)
- Affected code: frontend/src/components/modern_main_frame.py, frontend/src/components/attendance_section_optimized.py, frontend/public/locales/*.json, models.py (existing tables reused)
