## ADDED Requirements

### Requirement: カレンダー日付選択
The system SHALL 全ての日付フィールドにカレンダーピッカーを提供し、手入力を禁止する。

#### Scenario: Daily report date
- **GIVEN** 利用者が日報ページにいる
- **WHEN** 利用者が日付を選択する
- **THEN** 日付はカレンダーピッカーでのみ入力される

#### Scenario: Date filters
- **GIVEN** 利用者が Delay List または Summary Actual ページにいる
- **WHEN** 開始/終了日を選択する
- **THEN** 日付はカレンダーピッカーで入力される

#### Scenario: Edit dialogs
- **GIVEN** Delay または Summary Actual の行を編集する
- **WHEN** 日付を更新する
- **THEN** 日付はカレンダーピッカーで選択される
