# 多語言支持功能介面約定

本系統為單機桌面應用，無 REST API；以下為語言管理內部介面約定。

## 1. LanguageManager

### set_language(language_code: str) -> None
- **目的**: 切換當前語言
- **參數**: language_code ∈ {"ja", "zh", "en"}

### get_current_language() -> str
- **目的**: 取得目前語言

### get_text(key: str, default: str) -> str
- **目的**: 取得語言文字，缺鍵時回退 default

## 2. UI 更新流程
- 語言切換後，由頁面 `update_language()` 或等效方法更新介面文字。
- 缺少翻譯鍵時需顯示預設文字，避免空白。
