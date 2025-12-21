# 實施計劃 (Implementation Plan)

## 1. 技術背景 (Technical Context)
- **應用形式**: 單機桌面應用程式 (無前後端 API)
- **UI 框架**: Python tkinter
- **資料庫**: SQLite + SQLAlchemy
- **多語言**: JSON 語言資源檔 + LanguageManager
- **認證**: bcrypt 密碼雜湊
- **報表匯入**: pandas / openpyxl
- **圖表**: matplotlib (出勤統計)
- **設定保存**: `handover_settings.json`

## 2. 憲法檢查 (Constitution Check)
根據專案憲法原則，本計劃需確保：
- 代碼品質：介面與資料邏輯結構清楚、可讀
- 安全性：密碼雜湊與管理員權限控制
- 可擴展性：模組化頁面，便於新增或調整頁面
- 可維護性：文件與語言資源維護一致
- 數據保護：SQLite 資料可備份、可復原

## 3. 評估門檻 (Gates)
- [x] 資料模型符合需求規格
- [x] 日報表與出勤/異常資料關聯一致
- [x] 多語言與文案維護流程明確
- [x] 單機部署與備份流程可行

## 4. 第一階段：研究與決策 (Phase 0)
本階段已完成，研究結果記錄於 `research.md`：
- 選用 tkinter + SQLite 架構
- 多語言採 JSON 資源檔
- 圖表採 matplotlib

## 5. 第二階段：設計與合約 (Phase 1)
- 數據模型記錄於 `data-model.md`
- 介面與流程說明記錄於 `quickstart.md`
- 內部介面與資料存取約定記錄於 `contracts/api-contracts.md`

## 6. 實施任務 (Implementation Tasks)
詳細任務與當前狀態記錄於 `tasks.md`。

## 7. 測試策略 (Testing Strategy)
- 單元測試：核心資料存取與驗證
- 整合測試：登入 → 基本資訊 → 功能填寫流程
- 可用性測試：多語切換與操作一致性

## 8. 部署考量 (Deployment Considerations)
- 使用 PyInstaller 打包為可執行檔
- SQLite/JSON 設定檔需納入備份
- 初次啟動需初始化資料庫與管理員帳號
