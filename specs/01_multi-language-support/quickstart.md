# 多語言支持 - 快速入門

## 1. 語言資源位置
- `frontend/public/locales/ja.json`
- `frontend/public/locales/zh.json`
- `frontend/public/locales/en.json`

## 2. 使用 LanguageManager

```python
from frontend.main import LanguageManager

lang_manager = LanguageManager()
lang_manager.set_language("zh")
text = lang_manager.get_text("common.save", "儲存")
```

## 3. 介面更新
- 語言切換後呼叫各頁面的 `update_language()`
- 缺少翻譯鍵時使用預設文字

## 4. 管理員維護
- 透過管理頁面匯入/匯出 JSON
- 匯出後覆蓋 `frontend/public/locales/*.json`
