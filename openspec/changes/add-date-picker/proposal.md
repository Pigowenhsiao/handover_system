# Change: 全ての日付入力にカレンダー選択を追加

## Why
現行は日付を手入力する必要があり、形式ミスが発生しやすく、「直接入力しない」運用要件に合致しない。

## What Changes
- 日報の日付はカレンダー選択に変更し、手入力を禁止。
- Delay List と Summary Actual の日付範囲はカレンダー選択に変更。
- Delay List と Summary Actual の編集ダイアログの日付もカレンダー選択に変更。
- 共通のカレンダーポップアップと多言語文言を追加。

## Impact
- Affected specs: ui-calendar (new)
- Affected code: frontend/src/components/modern_main_frame.py, frontend/public/locales/*.json
