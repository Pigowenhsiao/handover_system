# 多言語対応 - クイックスタート

## 1. 言語リソースの場所
- `frontend/public/locales/ja.json`
- `frontend/public/locales/zh.json`
- `frontend/public/locales/en.json`

## 2. LanguageManager の使用

```python
from frontend.main import LanguageManager

lang_manager = LanguageManager()
lang_manager.set_language("zh")
text = lang_manager.get_text("common.save", "保存")
```

## 3. UI 更新
- 言語切替後に各ページの `update_language()` を呼び出す
- 翻訳キーが欠落した場合は既定文言を使用

## 4. 管理者による維持
- 管理画面から JSON をインポート/エクスポート
- エクスポート後に `frontend/public/locales/*.json` を上書き
