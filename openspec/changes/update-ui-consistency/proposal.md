# Change: デスクトップ UI の一貫性と多言語整合を改善

## Why
現行 UI はレイアウト、文言リソース、言語切替に不整合やハードコードがあり、使いやすさと保守性が低下している。

## What Changes
- フォーム/操作ブロックのレイアウトと余白規則を統一し、可読性と一貫性を向上。
- 多言語リソースを補完/統一し、ハードコード文字列を除去。
- 入力欄の枠線を明確にし、Text/Entry/Combobox の視認性を改善。
- UI 操作フローと状態表示を整理し、ログイン/ログアウトと機能可用性を直感的に。
- 各ページの操作ロジックを一般的な操作感に合わせる（例：Enter でログイン）。

## Impact
- Affected specs: `desktop-ui`
- Affected code: `frontend/src/components/modern_main_frame.py`, `frontend/src/components/*`, `frontend/main.py`, `frontend/public/locales/*.json`
