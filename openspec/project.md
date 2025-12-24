# Project Context

## Purpose
単機版の電子引き継ぎ帳および多言語管理システム。紙/PDF の日報を置き換え、Tkinter によるデスクトップ GUI で翻訳資源管理、日/中/英の切替、ログイン、出勤、設備異常、異常ロット、総結、写真アップロード等の機能を提供する。目標はオフライン運用とインストールの容易さで、配布/保守コストを下げること。

## Tech Stack
- 言語：Python 3.9+
- GUI：Tkinter / ttk（デスクトップアプリ、リサイズ対応）
- DB：SQLite（ローカルファイル）
- ORM：SQLAlchemy
- 認証：bcrypt（ローカルのパスワードハッシュ）
- データ処理：pandas、openpyxl（Excel インポート）
- グラフ：matplotlib（Tkinter へ埋め込み）
- テスト/検証：`verify_features.py`、`verify_implementation.py`、`tests/` 内スクリプト

## Project Conventions

### Code Style
- Python 標準スタイル（PEP8）を基本とし、必要時のみ簡潔なコメントを付与。
- 標準ライブラリ優先、不要な外部依存は避ける。

### Entry Point
- 現代化介面啟動入口為 `handover_system.py`（建議使用）。

### Architecture Patterns
- 単機デスクトップアプリ：UI/DB ともにローカル実行。
- 分層：UI（Tkinter）、アプリ層（業務ロジック/検証）、データ層（SQLAlchemy + SQLite）。
- 認証：パスワードはハッシュ保存、ログイン状態は UI 状態で管理。

### Testing Strategy
- 軽量検証スクリプト：`verify_features.py`、`verify_implementation.py`。
- 自動テスト：`tests/` 内スクリプト。
- 手動確認：言語切替、日報/統計フロー、Excel インポート/アップロード、管理機能。
- CI はなし。ローカル実行と手動確認が中心。

### Git Workflow
- 主幹ブランチで開発。必要なら機能名のブランチ（kebab-case）。
- コミットは変更内容が分かる短いメッセージ（例：`fix-lang-import-null`、`add-attendance-ui`）。

## Domain Context
- 対象ユーザー：管理者および一般ユーザー。管理者は翻訳/交接データを管理。
- オフライン運用：ネットワーク依存なし。データはローカル SQLite。
- 翻訳は GUI からインポート/更新でき、即時反映。

## Functional Requirements 概要
- ログイン後、日報の基本情報（日時/シフト/エリア）を保存するまで出勤/設備異常/異常ロット/管理などの操作は不可。ただし出勤率/摘要查詢/異常履歴はログイン後であれば基本情報未保存でも閲覧可能。
- 同一 日付+シフト+エリア は同一日報として上書き。
- 基本情報：日付はカレンダー選択。シフト選択 [Day, Night]。エリア選択 [etching_D, etching_E, litho, thin_film]。記入者はログインユーザーを自動反映。
- 出勤：正社員/契約社員の定員、出勤、欠勤、理由。
- 設備異常：設備番号、異常内容、発生時刻、影響数、対応内容、画像パス（任意）。
- 異常ロット：ロット番号、異常内容、処置状況、特記事項。
- 総結：出勤統計（表 + 出勤率折線図 + 出勤人数積み上げ棒グラフ）。期間は当月 1 日〜本日。
- 異常履歴：設備異常/異常ロットの履歴照会（二表）、期間とシフト/エリアの絞り込み。
- レポート取込：Delay List / Summary Actual の Excel インポート → 仮保存 → アップロード。

## Data Model (SQLAlchemy Models)
- User：`id`、`username`（一意）、`password_hash`、`role`（admin/user）。
- ShiftOption：`id`、`name`（Day/Night 等）。
- AreaOption：`id`、`name`（etching_D、etching_E、litho、thin_film 等）。
- DailyReport：`id`、`date`、`shift`、`area`、`author_id`、`created_at`、`last_modified_by`、`last_modified_at`、`summary_key_output`、`summary_issues`、`summary_countermeasures`。
- AttendanceEntry：`id`、`report_id`、`category`（Regular/Contract）、`scheduled_count`、`present_count`、`absent_count`、`reason`。
- OvertimeEntry：`id`、`report_id`、`category`、`count`、`notes`。
- EquipmentLog：`id`、`report_id`、`equip_id`、`description`、`start_time`、`impact_qty`、`action_taken`、`image_path`（任意）。
- LotLog：`id`、`report_id`、`lot_id`、`description`、`status`、`notes`。
- DelayEntry：`id`、`delay_date`、`time_range`、`reactor`、`process`、`lot`、`wafer`、`progress`、`prev_steps`、`prev_time`、`severity`、`action`、`note`。
- SummaryActualEntry：`id`、`summary_date`、`label`、`plan`、`completed`、`in_process`、`on_track`、`at_risk`、`delayed`、`no_data`、`scrapped`。

## UI/UX レイアウト
- ログイン画面：ログイン後に主画面へ。
- 主画面：左サイドナビ + 右コンテンツ（カード UI）。
- 表：`ttk.Treeview` を使用。ダブルクリックで編集。
- ファイル入出力：`filedialog` で Excel/画像を選択し SQLite へ保存。
- グラフ：matplotlib を Tkinter に埋め込み表示。

## Important Constraints
- ネットワークやクラウドは使用しない。
- Python 3.9+ 互換を維持。
- UI と DB は同一プロジェクト配下で配置。DB は既定で `data/handover_system.db`、設定 (`handover_settings.json`) でパス変更可能。

## External Dependencies
- 無外部 API 或服務；依賴本機套件：SQLAlchemy、pandas、openpyxl、matplotlib、bcrypt（Tkinter 為 Python 內建）。
