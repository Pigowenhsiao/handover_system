# 電子引き継ぎシステム実施計画 (Implementation Plan)

## 1. 現況概要
- 単機デスクトップアプリ (Tkinter)
- SQLite ローカル DB + SQLAlchemy
- 多言語リソースは JSON で管理
- コア機能はモダン UI に統合済み

## 2. 完了済みモジュール
- ログインと権限制御
- 日報基本情報 (日付/シフト/エリア) のゲート
- 出勤/設備異常/ロット異常/Delay List/Summary Actual
- 出勤統計と異常履歴照会
- 管理者：ユーザー、翻訳、シフト/エリア
- システム設定：バックアップ間隔の保存
- テーマ切替：ライト/ダークと設定保存

## 3. ドキュメントと規約
- 仕様：`specs/` と `openspec/`
- 操作説明：`README.md`, `docs/user_manual.md`, `docs/admin_guide.md`

## 4. 保守ポイント
- 仕様書は実装と整合させて更新する
- 翻訳リソースの入出力後は言語ファイル整合を確認
- `data/handover_system.db` と `handover_settings.json` の定期バックアップ
