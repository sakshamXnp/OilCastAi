# OilCast AI - Startup Script
# This script starts the backend and frontend servers in separate windows.
# They will continue to run even after closing the Antigravity tool.

Write-Host "--- Initializing OilCast AI Services ---" -ForegroundColor Cyan

# 1. Start Backend on Port 3001
Write-Host "Launching Backend on Port 3001..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; $env:PYTHONPATH='.'; .\venv\Scripts\python.exe -m uvicorn main:app --reload --port 3001 --host 0.0.0.0" -WindowStyle Minimized

# 2. Start Frontend on Port 3000
Write-Host "Launching Frontend on Port 3000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npx next dev --port 3000" -WindowStyle Minimized

Write-Host "----------------------------------------" -ForegroundColor Cyan
Write-Host "Servers are now running in the background." -ForegroundColor White
Write-Host "Backend: http://localhost:3001" -ForegroundColor Gray
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Gray
Write-Host "You can safely close this window and the Antigravity tool." -ForegroundColor Yellow
