# Change: 新增異常設備與異常批次歷史查詢

## Why
現有系統只有單筆新增與列表視窗，缺少日期區間的歷史查詢，管理者無法快速檢索與彙整異常資料。

## What Changes
- 新增「異常歷史查詢」頁面（風格類似總結/出勤統計），提供日期區間與查詢按鈕。
- 顯示兩個表格：設備異常歷史與異常批次歷史，僅表格無圖表。
- 表格包含所有輸入細節，並顯示日報的日期/班別/區域與填寫者。
- 日期區間預設為當月第一天到今天。
- 新增/更新多語資源鍵。

## Impact
- Affected specs: `abnormal-history`
- Affected code: `frontend/src/components/modern_main_frame.py`, `frontend/public/locales/*.json`
