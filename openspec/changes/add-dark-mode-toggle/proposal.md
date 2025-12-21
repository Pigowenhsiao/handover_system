# Change: Add light/dark theme toggle in main UI

## Why
Windows 明亮模式下按鈕與文字對比不足，影響可讀性與操作辨識度，需要黑暗模式提升可視性。

## What Changes
- 在主畫面工具列提供明亮/黑暗主題切換按鈕
- 加入黑暗主題色盤，並套用到主要介面元件（背景、文字、按鈕、輸入框、卡片、狀態列）
- 切換時即時更新目前畫面

## Impact
- Affected specs: specs/main/spec.md
- Affected code: frontend/src/components/modern_main_frame.py, frontend/src/utils/theme_manager.py, frontend/public/locales/*.json
