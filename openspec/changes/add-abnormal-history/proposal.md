# Change: 設備異常/ロット異常の履歴照会を追加

## Why
現行は単発追加と一覧のみで、期間指定の履歴照会がなく、管理者が異常データを素早く検索/集計できない。

## What Changes
- 「異常履歴照会」ページを追加（出勤統計に近いレイアウト）。期間指定と検索ボタンを提供。
- 設備異常履歴とロット異常履歴の二表を表示（グラフなし）。
- 表には入力詳細と日報の日時/シフト/エリア/記入者を表示。
- 期間の既定は当月1日〜本日。
- 多言語リソースを追加/更新。

## Impact
- Affected specs: `abnormal-history`
- Affected code: `frontend/src/components/modern_main_frame.py`, `frontend/public/locales/*.json`
