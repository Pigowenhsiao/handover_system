## ADDED Requirements
### Requirement: ライト/ダークテーマ切替
システム SHALL 主画面にライト/ダークのテーマ切替を提供し、主要 UI 要素へ即時適用して可読性を高める。

#### Scenario: Switch to dark theme
- **WHEN** ユーザーがテーマ切替ボタンでダークモードに切替
- **THEN** 背景/文字/主要コントロールの配色が即時にダークテーマへ更新される

#### Scenario: Switch to light theme
- **WHEN** ユーザーが再度ボタンを押しライトモードに切替
- **THEN** 画面配色が即時にライトテーマへ戻る

### Requirement: テーマ設定の保存
システム SHALL 選択したテーマを保存し、次回起動時に適用する（既定はライト）。

#### Scenario: Persist selected theme
- **WHEN** ユーザーがテーマを切替
- **THEN** テーマ設定がローカル設定に保存される

#### Scenario: Restore theme on startup
- **WHEN** 起動時に設定ファイルにテーマが存在する
- **THEN** そのテーマで UI を初期化する
