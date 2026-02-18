@echo off
TITLE UPSC SAGA COMMANDER

echo =================================================
echo        STARTING UPSC SAGA: RAGNAROK EDITION
echo =================================================

:: Start Backend in a new window
echo Starting Backend (Flask)...
start "UPSC Backend" cmd /k "cd backend && python wsgi.py"

:: Start Frontend in a new window
echo Starting Frontend (Vite)...
start "UPSC Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Both realms are opening...
echo Go to: http://localhost:5173
echo.
pause