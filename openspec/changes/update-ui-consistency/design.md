## Context
桌面版同時存在舊版與現代化 UI，且多語文字來源分散，導致 UI 佈局與文案不一致。

## Goals / Non-Goals
- Goals: 統一畫面布局與間距規則、用語一致、語言切換後完整更新、操作狀態清楚。
- Non-Goals: 不改變資料庫結構、不新增外部服務、不引入新框架。

## Decisions
- Decision: 定義「標題區/內容區/操作區」的通用排列與間距，現代化 UI 統一採用。
- Decision: 所有可見文案改以語言鍵驅動；`frontend/public/locales/*.json` 補齊對應鍵。
- Decision: 登入狀態控制管理功能可見/可用，狀態列統一使用語言鍵與狀態圖示。
- Decision: 類似功能（如報表中的 Delay List / Summary Actual 按鈕）排列需保持一致邏輯與布局。

## Risks / Trade-offs
- 語言鍵變動可能造成漏翻譯 → 加入鍵檢查與逐頁驗證。

## Migration Plan
- 先整理語言鍵與缺漏清單 → 逐頁替換硬編碼字串 → 更新語言切換刷新邏輯。

## Open Questions
- 是否需要清理未使用的舊版 UI 檔案以避免混淆？
