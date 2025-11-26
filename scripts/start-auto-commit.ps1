# Quick start script for auto-commit to GitHub
# This will run the auto-commit watcher in the background

$scriptPath = Join-Path $PSScriptRoot "auto-commit-github.ps1"
$projectPath = "C:\Users\ACHARYS\Desktop\AISOC"

Write-Host "Starting auto-commit watcher..." -ForegroundColor Cyan
Write-Host "This will run in the background and auto-commit changes to GitHub" -ForegroundColor Yellow
Write-Host ""

# Start the script in a new window so it runs independently
Start-Process powershell -ArgumentList "-NoExit", "-File", "`"$scriptPath`"", "-WatchPath", "`"$projectPath`""

Write-Host "Auto-commit watcher started in a new window!" -ForegroundColor Green
Write-Host "You can close this window. The watcher will continue running." -ForegroundColor Yellow
Write-Host ""
Write-Host "To stop the watcher, close the other PowerShell window or press Ctrl+C in it." -ForegroundColor Gray

