@echo off
cd /d "e:\Oil\oilcast-ai"
echo Starting OilCast AI Monitoring Platform...
powershell.exe -ExecutionPolicy Bypass -File "./start_background_services.ps1"
echo Services are now running in the background (Bound to 127.0.0.1).
echo Backend: http://localhost:3001
echo Frontend: http://localhost:3000
echo Check logs/startup.log if you have issues.
pause
