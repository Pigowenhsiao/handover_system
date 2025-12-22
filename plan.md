# 実施計画 (Implementation Plan)

## 1. 技術背景 (Technical Context)
- **アプリ形態**: 単機デスクトップアプリ（前後端 API なし）
- **UI フレームワーク**: Python Tkinter
- **データベース**: SQLite + SQLAlchemy
- **多言語**: JSON 言語リソース + LanguageManager
- **認証**: bcrypt パスワードハッシュ
- **レポート取込**: pandas / openpyxl
- **チャート**: matplotlib（出勤統計）
- **設定保存**: `handover_settings.json`

## 2. 憲法チェック (Constitution Check)
本計画は以下を満たす必要があります：
- コード品質：UI とデータ処理の構造が明確で可読性が高いこと
- セキュリティ：パスワードハッシュと管理者権限制御
- 拡張性：ページのモジュール化による変更容易性
- 保守性：ドキュメントと翻訳リソースの一貫性
- データ保護：SQLite のバックアップ/復旧が可能

## 3. 評価ゲート (Gates)
- [x] データモデルが要件に適合
- [x] 日報と出勤/異常データの関連が一貫
- [x] 多言語と文言管理の流れが明確
- [x] 単機配布とバックアップ手順が成立

## 4. 第1段階：調査と意思決定 (Phase 0)
調査結果は `research.md` に記録済み：
- tkinter + SQLite 構成を採用
- 多言語は JSON リソースを採用
- チャートは matplotlib を採用

## 5. 第2段階：設計と契約 (Phase 1)
- データモデル：`data-model.md`
- 画面/フロー：`quickstart.md`
- 内部インターフェース：`contracts/api-contracts.md`

## 6. 実装タスク (Implementation Tasks)
詳細タスクと状況は `tasks.md` に記載。

## 7. テスト戦略 (Testing Strategy)
- 単体テスト：コアのデータ処理と検証
- 統合テスト：ログイン → 基本情報 → 機能入力の流れ
- 使いやすさテスト：多言語切替と操作の一貫性

## 8. 配布/導入 (Deployment Considerations)
- PyInstaller で実行ファイル化（`pyinstaller handover_modern.spec`）
- SQLite/JSON 設定ファイルをバックアップ対象に含める
- 初回起動時に DB と管理者アカウントを初期化
