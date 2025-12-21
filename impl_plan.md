# 電子交接系統實施計劃 (Implementation Plan)

## 1. 現況摘要
- 單機桌面應用 (tkinter)
- SQLite 本機資料庫 + SQLAlchemy
- 多語言資源以 JSON 檔案維護
- 核心功能已完成並整合至現代化 UI

## 2. 已完成模組
- 登入與權限控管
- 日報表基本資訊 (日期/班別/區域) 門檻
- 出勤/設備異常/批次異常/Delay List/Summary Actual
- 出勤統計與異常歷史查詢
- 管理員：使用者、翻譯、班別/區域
- 系統設定：備份間隔保存

## 3. 文件與規範
- 系統規格：`specs/` 與 `openspec/`
- 使用說明：`README.md`, `docs/user_manual.md`, `docs/admin_guide.md`

## 4. 維護重點
- 規格文件需與實際行為同步更新
- 翻譯資源匯入/匯出後須確認語言檔一致
- 定期備份 `data/handover_system.db` 與 `handover_settings.json`

