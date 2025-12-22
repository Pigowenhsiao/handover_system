# 多言語対応 内部インターフェース

本システムは単機デスクトップアプリであり、REST API は提供しません。以下は言語管理の内部インターフェース規約です。

## 1. LanguageManager

### set_language(language_code: str) -> None
- **目的**: 現在の言語を切替
- **引数**: language_code ∈ {"ja", "zh", "en"}

### get_current_language() -> str
- **目的**: 現在の言語を取得

### get_text(key: str, default: str) -> str
- **目的**: 翻訳文言を取得。キー欠落時は default を使用

## 2. UI 更新フロー
- 言語切替後は各ページの `update_language()` 等で UI を更新。
- 翻訳キーがない場合は既定文言を表示し、空欄を避ける。
