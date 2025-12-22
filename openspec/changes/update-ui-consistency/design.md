## Context
デスクトップ版に旧 UI とモダン UI が共存し、文言リソースが分散しているため、レイアウトと文言に不整合が発生している。

## Goals / Non-Goals
- Goals: レイアウト/余白規則の統一、文言の統一、言語切替後の完全更新、状態表示の明確化。
- Non-Goals: DB 構造の変更なし、外部サービス追加なし、新フレームワーク導入なし。

## Decisions
- Decision: 「タイトル/コンテンツ/操作」領域の共通レイアウトと余白を定義し、モダン UI に統一適用。
- Decision: すべての文言は言語キーで管理し、`frontend/public/locales/*.json` を補完。
- Decision: ログイン状態で管理機能の表示/利用を制御し、ステータス表示は言語キーとアイコンで統一。
- Decision: 類似機能（Delay List / Summary Actual など）のボタン配置と並びを統一。

## Risks / Trade-offs
- 言語キー変更により翻訳漏れの可能性 → キー検査とページ単位検証を追加。

## Migration Plan
- 言語キー/欠落リストを整理 → ハードコード文字列を順次置換 → 言語切替の更新ロジックを調整。

## Open Questions
- 不要な旧 UI ファイルを削除して混乱を防ぐべきか？
