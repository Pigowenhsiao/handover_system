# 多語言功能說明

## 概述
本系統為單機桌面應用，無 REST API。多語言資源採本機 JSON 檔，並由 LanguageManager 載入與切換。

- 支援語言：日文 (ja)、中文 (zh)、英文 (en)
- 語言檔位置：`frontend/public/locales/*.json`
- 預設語言：日文

## 資源結構
JSON 採巢狀結構，範例：
```json
{
  "header": {
    "title": "電子交接系統",
    "languageSwitch": "語言切換"
  },
  "common": {
    "save": "儲存",
    "cancel": "取消"
  }
}
```

## 切換流程
1. 使用者在登入畫面或主畫面選擇語言。
2. LanguageManager 即時更新文字，畫面同步刷新。
3. 若鍵值缺失，使用預設文字作為回退。

## 管理者維護方式
- 管理頁面提供翻譯資源匯入/匯出功能。
- 建議流程：匯入 → 調整 → 匯出 → 覆蓋 `frontend/public/locales/*.json`。

## 注意事項
- 目前語言選擇為單次會話記憶，重新啟動會回到預設日文。
- 圖表中文字體使用 CJK 字型回退，避免中文/日文亂碼。
