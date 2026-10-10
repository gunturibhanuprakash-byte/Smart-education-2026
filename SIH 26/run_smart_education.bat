@echo off
title Smart Education - Personalized Learning Platform
echo ========================================================
echo   Starting Smart Education Platform (Port 5001)
echo ========================================================
echo.
echo Opening http://localhost:5001 in your browser...
start http://localhost:5001
echo.
echo Starting Python Flask Server on Port 5001...
python app.py
pause
