@echo off
title AttendPro – Student Attendance System
echo.
echo =====================================================
echo   AttendPro - Student Attendance Management System
echo =====================================================
echo.
echo [1/2] Installing dependencies...
pip install Flask==3.0.3 Werkzeug==3.0.3
echo.
echo [2/2] Starting server...
echo.
echo  Open your browser at: http://127.0.0.1:5000
echo  Login:  admin / admin123   OR   teacher1 / teacher123
echo  Press Ctrl+C to stop the server.
echo.
python app.py
pause
