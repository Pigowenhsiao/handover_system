# 開發任務清單 (Tasks)

## 專案：電子交接本系統 (Handover System)

此清單對齊現行單機桌面版，標記已完成的核心功能與後續維護項目。

## Phase 1: 基礎設施 (Infrastructure)
- [x] SQLite + SQLAlchemy 連線與模型建立 (`models.py`)
- [x] 初始化管理員與預設班別/區域
- [x] 本機設定檔讀寫 (`handover_settings.json`)

## Phase 2: 核心功能 (Core Features)
- [x] 登入流程與角色控制
- [x] 基本資訊 (日期/班別/區域) 儲存門檻
- [x] 日報表摘要欄位儲存
- [x] 出勤記錄 (正職/契約同頁輸入)
- [x] 設備異常記錄
- [x] 異常批次記錄
- [x] Delay List / Summary Actual 匯入與上傳

## Phase 3: 介面與統計 (UI & Analytics)
- [x] 現代化側邊欄 UI (`modern_main_frame.py`)
- [x] 多語切換與語言資源管理
- [x] 出勤統計表 + 折線圖 + 堆疊柱狀圖
- [x] 異常歷史查詢 (設備/批次)
- [x] 頁面滾動與一致化版面

## Phase 4: 系統管理 (Admin)
- [x] 使用者管理 (新增/更新/刪除/重設密碼)
- [x] 翻譯資源管理 (匯入/匯出)
- [x] 班別/區域管理
- [x] 系統設定 (備份間隔)

## Phase 5: 測試與封裝 (Testing & Packaging)
- [x] 測試腳本結構 (`tests/`)
- [x] 打包腳本 (`scripts/build_executable.py`)

## Phase 6: 文件 (Documentation)
- [x] README / Quickstart / Spec 文件對齊現況
- [x] 使用者與管理者操作手冊
