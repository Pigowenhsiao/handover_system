# クイックスタート (Main Spec Quickstart)

## システム要件
- Python 3.9+
- Tkinter（標準搭載）
- SQLite（標準搭載）

## インストールと起動
```bash
pip install -r requirements.txt
python handover_system.py
```

既定の管理者アカウント：`admin` / `admin123`

## 基本フロー
1. ログインして言語を選択
2. 日報の基本情報を保存（日付/シフト/エリア）
3. 出勤、設備異常、ロット異常、出勤統計、異常履歴を操作

## データと設定
- SQLite：`data/handover_system.db`
<<<<<<< Updated upstream
- システム設定：`handover_settings.json`
=======
- 系統設定：`handover_settings.json`


>>>>>>> Stashed changes
