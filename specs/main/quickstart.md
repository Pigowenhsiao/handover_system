# 快速入門 (Main Spec Quickstart)

## 系統需求
- Python 3.9+
- Tkinter（系統內建）
- SQLite（系統內建）

## 安裝與啟動
```bash
pip install -r requirements.txt
python run_modern_system.py
```

預設管理員帳號：`admin` / `admin123`

## 基本流程
1. 登入並選擇語言
2. 日報表儲存基本資訊（日期/班別/區域）
3. 進行出勤、設備異常、異常批次、總結與歷史查詢

## 資料與設定
- SQLite：`data/handover_system.db`
- 系統設定：`handover_settings.json`

