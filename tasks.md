# 開発タスクリスト (Tasks)

## プロジェクト：電子引き継ぎシステム

本リストは現行の単機デスクトップ版に合わせた完了状況と保守項目を示します。

## Phase 1: 基盤 (Infrastructure)
- [x] SQLite + SQLAlchemy 接続とモデル定義 (`models.py`)
- [x] 管理者と既定のシフト/エリア初期化
- [x] ローカル設定の読み書き (`handover_settings.json`)

## Phase 2: コア機能 (Core Features)
- [x] ログインフローと権限制御
- [x] 基本情報 (日付/シフト/エリア) の保存ゲート
- [x] 日報サマリー欄の保存
- [x] 出勤記録 (正社員/契約社員を同ページ入力)
- [x] 設備異常記録
- [x] 異常ロット記録
- [x] Delay List / Summary Actual のインポートとアップロード

## Phase 3: UI と統計 (UI & Analytics)
- [x] モダンなサイドバー UI (`modern_main_frame.py`)
- [x] 多言語切替と言語リソース管理
- [x] 出勤統計表 + 折線図 + 積み上げ棒グラフ
- [x] 異常履歴照会（設備/ロット）
- [x] 画面スクロールとレイアウト統一

## Phase 4: システム管理 (Admin)
- [x] ユーザー管理 (追加/更新/削除/パスワードリセット)
- [x] 翻訳リソース管理（インポート/エクスポート）
- [x] シフト/エリア管理
- [x] システム設定（バックアップ間隔）

## Phase 5: テストとパッケージ (Testing & Packaging)
- [x] テストスクリプトの整備 (`tests/`)
- [x] パッケージスクリプト (`scripts/build_executable.py`)

## Phase 6: ドキュメント (Documentation)
- [x] README / Quickstart / Spec を現況に合わせ更新
- [x] 利用者・管理者マニュアル
