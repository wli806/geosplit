@echo off
chcp 65001 >nul
title feasibility launcher (V2)
echo Starting V2 backend (8001) and frontend (5501)...

REM V2:后端 = api.app(五层结构),前端 = frontend
start "v2-backend"  cmd /k py -m uvicorn api.app:app --port 8001 --app-dir "%~dp0backend"
start "v2-frontend" cmd /k py -m http.server 5501 --directory "%~dp0frontend"

echo Waiting for backend to come up (max 25s)...
set /a tries=0
:wait
curl -s -o nul http://localhost:8001/ping
if %errorlevel%==0 goto ready
set /a tries+=1
if %tries% geq 25 goto giveup
timeout /t 1 >nul
goto wait

:ready
echo Backend up. Opening browser...
start http://localhost:5501
goto end

:giveup
echo.
echo [!] Backend did not respond in 25s. Check the "v2-backend" window for the error.
start http://localhost:5501

:end
echo.
echo Done. Keep BOTH terminal windows open while using the site.
echo (Stage 0 demo lives in backup/backend_stage0/ + backup/frontend_stage0/, no longer launched here.)
