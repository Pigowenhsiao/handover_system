@echo off
rem 電子交接本系統啟動腳本

echo 正在啟動電子交接本系統...
echo.

rem 檢查 Python 是否安裝
python --version > nul 2>&1
if errorlevel 1 (
    echo 錜您尚未安裝 Python。請先安裝 Python 3.9 或更高版本。
    pause
    exit /b 1
)

echo 使用 Python 版本:
python --version
echo.

rem 檢查當前目錄
echo 當前目錄: %cd%
echo.

rem 運行應用程式
echo 正在啟動應用程式...
python app.py

rem 如果 Python 執行失敗，顯示錯誤訊息
if errorlevel 1 (
    echo.
    echo 錯誤發生，請檢查錯誤訊息
    pause
)

pause
