# Change: 優化桌面 UI 佈局一致性與多語正確性

## Why
目前桌面版 UI 在版面、文字資源與語言切換上存在不一致與硬編碼情況，降低易用性與維護性。

## What Changes
- 統一各畫面表單與操作區塊的版面規則與間距，提升可讀性與一致性。
- 補齊並統一多語文字資源，移除硬編碼字串，確保切換語言後所有顯示正確。
- 調整 UI 操作邏輯與狀態顯示，使登入/登出與功能可用性更直觀。
- 檢查每一個頁面的操作邏輯更接近一般人使用的習慣（例如 Enter 可登入）。

## Impact
- Affected specs: `desktop-ui`
- Affected code: `frontend/src/components/modern_main_frame.py`, `frontend/src/components/*`, `frontend/main.py`, `frontend/public/locales/*.json`
