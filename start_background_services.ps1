# OilCast AI - Background Service Script
# Designed for execution via Task Scheduler

$RootDir = "e:\Oil\oilcast-ai"
$LogFile = Join-Path $RootDir "logs\startup.log"

# Ensure log directory exists
New-Item -ItemType Directory -Force -Path (Join-Path $RootDir "logs") | Out-Null

Write-Output "[$(Get-Date)] Starting background services..." | Out-File -FilePath $LogFile -Append

# 1. Start Backend on Port 3001
Write-Output "[$(Get-Date)] Launching Backend..." | Out-File -FilePath $LogFile -Append
Start-Process powershell -ArgumentList "-WindowStyle Hidden", "-Command", "cd backend; $env:PYTHONPATH='.'; .\venv\Scripts\python.exe -m uvicorn main:app --reload --port 3001 --host 0.0.0.0"

# 2. Start Frontend on Port 3000
Write-Output "[$(Get-Date)] Launching Frontend..." | Out-File -FilePath $LogFile -Append
Start-Process powershell -ArgumentList "-WindowStyle Hidden", "-Command", "cd frontend; npx next dev --hostname 127.0.0.1 --port 3000"

Write-Output "[$(Get-Date)] Services launched in hidden windows." | Out-File -FilePath $LogFile -Append
