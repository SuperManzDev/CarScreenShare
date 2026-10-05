@echo off
title Open Windows Firewall for Car Screen Share
echo ======================================================================
echo          OPENING FIREWALL FOR PORT 8080 (CAR SCREEN SHARE)
echo ======================================================================
echo.
echo Requesting administrator privileges to open port 8080...
echo.

netsh advfirewall firewall add rule name="Car Screen Share (Port 8080)" dir=in action=allow protocol=TCP localport=8080

if %errorlevel% equ 0 (
    echo.
    echo [SUCCESS] Port 8080 is now open on your local network!
) else (
    echo.
    echo [NOTE] Please right-click this file and select "Run as administrator" to apply firewall rule.
)

echo.
pause
