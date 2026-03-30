# Create Desktop Shortcut for OilCast AI
$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [System.Environment]::GetFolderPath('Desktop')
$Shortcut = $WshShell.CreateShortcut((Join-Path $DesktopPath "OilCast AI.lnk"))
$Shortcut.TargetPath = "e:\Oil\oilcast-ai\OilCast_Start.bat"
$Shortcut.WorkingDirectory = "e:\Oil\oilcast-ai"
$Shortcut.Description = "Start OilCast AI Background Services"
$Shortcut.Save()

Write-Host "--- Desktop Shortcut Created! ---" -ForegroundColor Green
Write-Host "You can now double-click 'OilCast AI' on your desktop to start the servers." -ForegroundColor White
Write-Host "This will keep the site running even after you close your tools." -ForegroundColor Yellow
