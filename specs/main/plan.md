# Main Spec 実装計画 (現況)

本プロジェクトは単機デスクトップアプリであり、以下は現行構成と技術背景のまとめです。

## 技術背景
- Language/Version: Python 3.9+
- GUI: Tkinter/ttk
- DB: SQLite（ローカル）
- ORM: SQLAlchemy
- Auth: bcrypt
- Chart: matplotlib（Tkinter 埋め込み）

## プロジェクト構成（現状）
```
handover_system/
<<<<<<< Updated upstream
├── run_modern_system.py          # モダン UI 起動器
├── handover_modern.spec          # PyInstaller パッケージ設定
=======
├── handover_system.py          # 現代化介面啟動器
>>>>>>> Stashed changes
├── models.py                     # SQLAlchemy models
├── auth.py                       # パスワードハッシュ/検証
├── frontend/
│   ├── main.py                   # 言語管理と UI 起動
│   └── src/
│       └── components/           # Tkinter UI コンポーネント
├── frontend/public/locales/      # 多言語リソース
├── data/handover_system.db            # SQLite DB（起動後生成）
└── handover_settings.json        # システム設定（起動後生成）
```

<<<<<<< Updated upstream
## 現況マイルストーン
- 多言語切替（日/中/英）完了
- 日報フロー、出勤、設備異常、ロット異常完了
- 出勤統計（表 + グラフ）完了
- 異常履歴照会（2表 + フィルタ）完了
- 管理機能（ユーザー/翻訳/シフト/エリア）完了
- テーマ切替（ライト/ダーク）完了
=======
## 現況里程碑
- 多語言切換（中/英/日）已完成
- 日報流程、出勤、設備異常、批次異常已完成
- 總結頁改為出勤統計（表格 + 圖表）已完成
- 異常歷史查詢（雙表格 + 篩選）已完成
- 管理功能（使用者/翻譯/班別/區域）已完成


>>>>>>> Stashed changes
