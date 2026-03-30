# OilCast AI - Task Registration Script

$TaskName = "OilCastAI_Server"
$ScriptPath = "e:\Oil\oilcast-ai\start_background_services.ps1"

# 1. Define the Action
$Action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-ExecutionPolicy Bypass -File $ScriptPath" -WorkingDirectory "e:\Oil\oilcast-ai"

# 2. Define the Trigger (One-time, but we'll start it manually)
$Trigger = New-ScheduledTaskTrigger -AtLogOn

# 3. Define the Settings (Allow manual start, run as soon as possible)
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# 4. Register the Task
Write-Host "Registering Task: $TaskName..." -ForegroundColor Cyan
try {
    # Check if task already exists
    if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    }
    Register-ScheduledTask -Action $Action -Trigger $Trigger -Settings $Settings -TaskName $TaskName -Description "Runs OilCast AI Backend and Frontend servers."
    Write-Host "Task registered successfully!" -ForegroundColor Green
    
    # Start the task immediately
    Write-Host "Starting services now..." -ForegroundColor Yellow
    Start-ScheduledTask -TaskName $TaskName
} catch {
    Write-Host "ERROR: Could not register task. You may need to run this script as Administrator." -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Gray
}
