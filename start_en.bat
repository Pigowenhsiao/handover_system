@echo off
rem Multilingual Support System Startup Script

echo Starting Multilingual Support System...
echo.

rem Check if Python is installed
python --version > nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python 3.9 or higher first.
    pause
    exit /b 1
)

echo Using Python version:
python --version
echo.

rem Check current directory
echo Current directory: %cd%
echo.

rem Run the application
echo Starting application...
python app.py

rem If Python execution fails, show error message
if errorlevel 1 (
    echo.
    echo An error occurred, please check error messages
    pause
)

pause
