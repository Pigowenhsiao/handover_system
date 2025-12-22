# Change: 総結ページを出勤統計ダッシュボードに更新

## Why
現行の総結ページはテキスト入力と仮データ中心で、管理者が必要とする出勤統計の可視化が不足している。

## What Changes
- 総結ページを「出勤統計」に変更。開始/終了日と「確定」ボタンを追加。
- 期間内の DailyReport + AttendanceEntry を集計し、表に「日付/エリア/正社員出勤/正社員欠勤/契約出勤/契約欠勤/備考」を表示。
- 下部に 2 つのグラフ：出勤率折線図（毎日の出勤率）と出勤人数の積み上げ棒グラフ（正社員/契約）。
- 中日文字化け防止のため CJK フォント設定とフォールバックを追加。
- 多言語キーを追加/更新。

## Impact
- Affected specs: `summary-dashboard`
- Affected code: `frontend/src/components/modern_main_frame.py`, `frontend/public/locales/*.json`
