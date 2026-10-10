@echo off
title Share Smart Education to Mobile / Any PC
echo ========================================================
echo   Sharing Smart Education to Mobile / Internet
echo ========================================================
echo.
echo Connecting public HTTPS tunnel to Smart Education (Port 5001)...
echo.
ssh -o StrictHostKeyChecking=no -R 80:127.0.0.1:5001 serveo.net
pause