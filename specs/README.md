# 電子引き継ぎシステム 仕様一覧

本ディレクトリには電子引き継ぎシステムの機能仕様をまとめています。

## 機能一覧

### 1. 多言語対応 (01_multi-language-support)
- **機能**: システムの多言語対応（日/中/英）
- **状態**: 完了
- **要点**: 言語選択により UI 表示が即時切替

### 2. ユーザー編集 (01_user-editor)
- **機能**: 管理者によるユーザーの追加/更新/削除
- **状態**: 完了
- **要点**: 管理画面からユーザー管理が可能

### 3. 多言語ラベル切替 (02_multilang-labels)
- **機能**: 言語切替時に UI ラベルが正しく更新
- **状態**: 完了
- **要点**: ラベルが言語選択に追随

### 4. 出勤記録改善 (03_attendance-enhancement)
- **機能**: 正社員/契約社員の出勤を同時に入力
- **状態**: 完了
- **要点**: 入力フローの簡略化

### 5. 主システム (main)
- **機能**: 日報、出勤、出勤統計、異常履歴、Delay List、Summary Actual、テーマ切替
- **状態**: 完了
- **要点**: 全機能を統合した本体仕様

## ファイル構成

```
specs/
├── 01_multi-language-support/     # 多言語対応の仕様
│   ├── spec.md
│   ├── plan.md
│   ├── research.md
│   ├── data-model.md
│   ├── quickstart.md
│   ├── contracts/
│   ├── tasks.md
│   └── checklists/
│       └── requirements.md
├── 01_user-editor/                # ユーザー編集仕様
│   ├── spec.md
│   └── checklists/
│       └── requirements.md
├── 02_multilang-labels/           # ラベル切替仕様
│   ├── spec.md
│   └── checklists/
│       └── requirements.md
├── 03_attendance-enhancement/     # 出勤記録改善仕様
│   ├── spec.md
│   └── checklists/
│       └── requirements.md
└── main/                          # 主システム仕様
    ├── spec.md
    ├── plan.md
    ├── research.md
    ├── data-model.md
    ├── quickstart.md
    ├── contracts/
    ├── tasks.md
    └── checklists/
        └── requirements.md
```

## 品質チェック

全ての仕様は以下の基準を満たすよう整理済み：
- 要件が明確でテスト可能
- 成功基準が測定可能
- 実装詳細を仕様に混在させない
- 主要なエッジケースを記載
- 主要ユーザーシナリオを網羅
