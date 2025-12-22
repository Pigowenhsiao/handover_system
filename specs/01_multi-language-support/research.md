# 多言語対応 調査 (Research)

## 1. 決定要約
- JSON ファイルを言語リソースとして使用
- LanguageManager で読み込みと切替
- Tkinter UI で即時更新

## 2. 方案比較
- **JSON + LanguageManager**: 軽量、保守容易、単機アプリに適合
- **gettext**: 標準だが設定/保守コストが高い

## 3. 結論
単機デスクトップ用途において、JSON + LanguageManager は最小依存で安定した多言語切替を提供できる。
