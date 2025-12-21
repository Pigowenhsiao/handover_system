# 多語言支持功能數據模型 (Data Model)

本系統多語言資源以 JSON 檔案形式儲存，不使用主 SQLite 資料庫表。

## 1. 語言資源檔 (Language Resource Files)
- 位置：`frontend/public/locales/*.json`
- 結構：巢狀鍵值對

範例：
```json
{
  "header": {
    "title": "電子交接系統",
    "login": "登入"
  },
  "common": {
    "save": "儲存",
    "cancel": "取消"
  }
}
```

## 2. 當前語言設定
- 由 LanguageManager 在執行期維護
- 預設語言為日文 (`ja`)
- 不進行跨次啟動持久化

## 3. 驗證規則
- 語言代碼限定 `ja`, `zh`, `en`
- 翻譯鍵應使用點號分層，避免重複
- 缺少鍵值時需回退預設文字
