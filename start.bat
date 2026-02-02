@echo off
:: %~dp0 代表「這個 bat 檔案所在的資料夾」
cd /d "%~dp0"

:: 寫個 Debug 紀錄
echo [Start-VENV] %date% %time% >> debug_run.log

:: 使用相對路徑呼叫 venv
if exist venv\Scripts\pythonw.exe (
    start "" venv\Scripts\pythonw.exe main.py
) else (
    echo [Error] Virtual environment not found. Please run 'python -m venv venv' first.
    pause
)

exit