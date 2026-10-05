@echo off
title CAR SCREEN STREAMER
color 0A
mode con: cols=75 lines=26
cls

echo =========================================================================
echo                    CAR SCREEN PC STREAMER
echo =========================================================================
echo.
echo  [+] Detecting network and starting screen streamer...
echo.

cd /d "C:\Users\MNZ\CarScreenShare"
python server.py

if %errorlevel% neq 0 (
    echo.
    echo  [!] Could not start streamer directly. Checking dependencies...
    python -m pip install mss pillow fastapi uvicorn pynput psutil
    python server.py
)

echo.
echo Stream stopped.
pause
