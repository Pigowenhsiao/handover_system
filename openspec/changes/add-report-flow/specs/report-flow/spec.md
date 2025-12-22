## ADDED Requirements

### Requirement: ログイン優先フロー
The system SHALL いかなる UI よりも先に単一のログイン画面を表示する。

#### Scenario: User not logged in
- **GIVEN** アプリが起動した
- **WHEN** ユーザーが未ログイン
- **THEN** ログイン画面のみ利用可能で、ナビゲーションは無効化される

#### Scenario: Successful login
- **GIVEN** ユーザーが正しい認証情報を入力した
- **WHEN** ログインが確認された
- **THEN** システムは基本情報画面を表示する

### Requirement: 基本情報ゲート
The system SHALL 日付/シフト/エリアの保存が完了するまで他機能を有効化しない。

#### Scenario: Access blocked before basic info
- **GIVEN** 基本情報が未保存
- **WHEN** ユーザーが出勤/設備/ロットのページを開こうとする
- **THEN** システムは操作をブロックし警告を表示する

#### Scenario: Access allowed after save
- **GIVEN** 基本情報が保存済み
- **WHEN** ユーザーが他ページを開く
- **THEN** ページが有効化され、現在の日報コンテキストが表示される

### Requirement: 日報コンテキストの表示
The system SHALL 全ページに現在の日報コンテキスト（日付/シフト/エリア）を表示する。

#### Scenario: Context updates
- **WHEN** ユーザーが日付/シフト/エリアを変更した
- **THEN** 表示中のコンテキストが即時更新される

### Requirement: DailyReport への紐付け
The system SHALL 出勤/設備/ロットの記録を DailyReport に report_id で紐付けて保存する。

#### Scenario: Attendance save
- **GIVEN** DailyReport が保存済み
- **WHEN** 出勤データを保存する
- **THEN** 出勤記録は report_id 付きで保存される

#### Scenario: Equipment and lot add
- **GIVEN** DailyReport が保存済み
- **WHEN** 設備またはロット記録を追加する
- **THEN** 各記録は report_id 付きで保存される
