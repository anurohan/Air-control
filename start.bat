@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo AirOS Python environment nahi mila:
    echo .venv\Scripts\python.exe
    echo Pehle project setup karke dobara try karein.
    pause
    exit /b 1
)

echo AirOS AI start ho raha hai...
"%~dp0.venv\Scripts\python.exe" -m app.main

if errorlevel 1 (
    echo.
    echo AirOS start nahi ho saka. Upar error check karein.
    pause
)

endlocal
