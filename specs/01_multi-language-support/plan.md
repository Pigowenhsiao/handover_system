# 多言語対応 実装計画 (Implementation Plan)

## 1. 技術背景 (Technical Context)
- **アプリ形態**: 単機デスクトップ (Tkinter)
- **翻訳リソース**: JSON + LanguageManager
- **対応言語**: 日本語 (ja), 英語 (en), 中文 (zh)
- **既定言語**: 日本語
- **文字方向**: LTR のみ

## 2. 憲法チェック (Constitution Check)
- コード品質：翻訳キーの集中管理
- セキュリティ：管理者のみ翻訳リソースを管理
- 拡張性：言語追加が可能
- 保守性：インポート/エクスポートで管理

## 3. 評価ゲート (Gates)
- [x] 翻訳リソース構造が保守可能
- [x] 言語切替の挙動が一貫
- [x] UI 文言が全体をカバー

## 4. 第1段階：調査と意思決定 (Phase 0)
- JSON を言語リソース形式に採用
- LanguageManager で即時切替を管理

## 5. 第2段階：設計と契約 (Phase 1)
- 仕様は `spec.md`
- クイックスタートは `quickstart.md`
- 内部契約は `contracts/api-contracts.md`

## 6. 実装タスク (Implementation Tasks)
詳細は `tasks.md` を参照。

## 7. テスト戦略 (Testing Strategy)
- 言語切替の動作確認
- 翻訳欠落のフォールバック確認
- UI 文言の整合性確認

## 8. 配布考慮 (Deployment Considerations)
- `frontend/public/locales/*.json` を同梱
- 翻訳キーの整合性を維持
