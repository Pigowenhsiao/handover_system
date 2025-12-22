# Change: メイン UI にライト/ダーク切替を追加

## Why
Windows のライトモードではボタンと文字のコントラストが不足し、可読性と操作性が低下するため、ダークモードで視認性を向上させる。

## What Changes
- 主画面のツールバーにライト/ダーク切替ボタンを追加
- ダークテーマの配色を追加し、主要 UI 要素（背景、文字、ボタン、入力欄、カード、ステータスバー）に適用
- 切替時に画面を即時更新
- テーマ設定を保存し、次回起動時に適用

## Impact
- Affected specs: specs/main/spec.md
- Affected code: frontend/src/components/modern_main_frame.py, frontend/src/utils/theme_manager.py, frontend/public/locales/*.json
