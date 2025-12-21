# 多語言支持功能研究 (Research)

## 1. 決策摘要
- 使用 JSON 檔案作為語言資源
- 以 LanguageManager 讀取與切換語言
- 在 tkinter 介面即時更新文字

## 2. 方案比較
- **JSON + LanguageManager**: 輕量、易維護、適合單機桌面
- **gettext**: 標準方案，但設定與維護成本較高

## 3. 結論
本專案為單機桌面應用，採用 JSON + LanguageManager 能以最少依賴達成穩定的多語切換與維護需求。
