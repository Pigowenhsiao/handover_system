# 多語言支持系統使用說明

## 概述
單機桌面應用，Python + SQLite，本機即可運行。支援日文/英文/中文即時切換，資料庫檔與應用同機，無需伺服器。

## 系統需求
- Python 3.9+
- 標準庫 (sqlite3, tkinter, threading, json, os, sys 等)
- 可讀寫本機 SQLite 檔案（無需外部資料庫服務）

## 快速開始
1) 安裝 Python 3.9+  
2) 下載專案、打開終端切到專案目錄  
3) 執行 `python main.py`（Windows 亦可雙擊 `start.bat`）  
4) 首次啟動會自動建立本機資料庫與預設管理員

常見入口：
- Windows：雙擊 `start.bat`
- 命令列：`python main.py`

## 功能說明

### 語言切換
- 主界面下拉選單選擇語言（日本語/中文/English）
- 介面立即切換並記住選擇

### 資源管理
- 點擊「管理」開啟翻譯資源介面
- 新增/編輯/刪除翻譯，支援搜尋與過濾

### 測試功能
- 「測試」按鈕可驗證翻譯鍵；可輸入翻譯鍵與預設值

### 匯入功能
- 「匯入」可讀取 JSON 檔（鍵值對）匯入翻譯資源

## 預設翻譯資源
內建常用界面翻譯：標題、按鈕、導航、通用術語。

## 數據庫
- 本機 `language_resources.db`（SQLite，無需遠端 DB）
- 主要表格：`language_resources`、`language_settings`、`language_packs`

## 技術架構
- 後端：Python + SQLite（本機資料庫檔案，單機部署）
- 前端：tkinter GUI
- 國際化：自定義翻譯管理系統
- 數據持久化：SQLite 資料庫（無需外部 DB 伺服器）

## 注意事項
1. 保持所有 Python 檔案在同一目錄
2. 首次啟動會自動建立資料庫與表
3. 關閉前請先儲存
4. 有狀況請查看終端訊息

## 組織結構
- `main.py`: 主入口點
- `language_manager.py`: 語言資源管理系統
- `gui_app.py`: 圖形用戶界面
- `language_resources.db`: 數據庫文件（運行後自動創建）
- `start.bat`: Windows 啟動腳本

## 疑難排解
如果應用程式未能啟動：
1. 確認已安裝 Python 3.9+
2. 檢查必要的 Python 檔案是否存在
3. 在終端執行 `python main.py` 觀察錯誤訊息
4. 確認沒有其他程式占用 `language_resources.db`
