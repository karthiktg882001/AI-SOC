# Auto-Commit and Push to GitHub Script
# This script watches for file changes and automatically commits and pushes them to GitHub

param(
    [int]$CommitDelay = 30,  # Wait 30 seconds after last change before committing
    [string]$WatchPath = "C:\Users\ACHARYS\Desktop\AISOC"
)

$ErrorActionPreference = "Continue"

# Change to project directory
Set-Location $WatchPath

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Auto-Commit to GitHub - Started" -ForegroundColor Cyan
Write-Host "Watching: $WatchPath" -ForegroundColor Cyan
Write-Host "Commit delay: $CommitDelay seconds" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Track last commit time to avoid too frequent commits
$lastCommitTime = Get-Date
$pendingChanges = $false
$commitTimer = $null

function Commit-And-Push {
    param([string]$Message)
    
    try {
        # Check if there are any changes
        $status = git status --porcelain
        if (-not $status) {
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] No changes to commit" -ForegroundColor Gray
            return
        }

        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Committing changes..." -ForegroundColor Yellow
        
        # Stage all changes
        git add -A
        
        # Commit with message
        $commitOutput = git commit -m $Message 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] ✓ Committed: $Message" -ForegroundColor Green
            
            # Push to GitHub
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Pushing to GitHub..." -ForegroundColor Yellow
            $pushOutput = git push origin main 2>&1
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "[$(Get-Date -Format 'HH:mm:ss')] ✓ Successfully pushed to GitHub!" -ForegroundColor Green
                Write-Host ""
            } else {
                Write-Host "[$(Get-Date -Format 'HH:mm:ss')] ✗ Push failed: $pushOutput" -ForegroundColor Red
            }
        } else {
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] ✗ Commit failed: $commitOutput" -ForegroundColor Red
        }
        
        $script:lastCommitTime = Get-Date
        $script:pendingChanges = $false
        
    } catch {
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] ✗ Error: $_" -ForegroundColor Red
    }
}

function Schedule-Commit {
    if ($script:commitTimer) {
        $script:commitTimer.Dispose()
    }
    
    $script:pendingChanges = $true
    
    # Create timer to commit after delay
    $script:commitTimer = New-Object System.Timers.Timer
    $script:commitTimer.Interval = $CommitDelay * 1000
    $script:commitTimer.AutoReset = $false
    $script:commitTimer.Add_Elapsed({
        if ($script:pendingChanges) {
            $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            $changedFiles = (git status --porcelain | Measure-Object -Line).Lines
            $message = "Auto-commit: $changedFiles file(s) changed at $timestamp"
            Commit-And-Push -Message $message
        }
        $script:commitTimer.Dispose()
        $script:commitTimer = $null
    })
    $script:commitTimer.Start()
}

# Create FileSystemWatcher
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $WatchPath
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true

# Filter out common files that shouldn't trigger commits
$excludePatterns = @(
    "\.git",
    "node_modules",
    "__pycache__",
    "\.pyc",
    "\.log",
    "\.tmp",
    "\.swp",
    "\.swo",
    "build/",
    "dist/",
    "target/",
    "\.idea",
    "\.vscode",
    "Thumbs\.db",
    "\.DS_Store"
)

function Should-Ignore {
    param([string]$Path)
    
    foreach ($pattern in $excludePatterns) {
        if ($Path -match $pattern) {
            return $true
        }
    }
    return $false
}

# Event handlers
$action = {
    $path = $Event.SourceEventArgs.FullPath
    $changeType = $Event.SourceEventArgs.ChangeType
    
    if (Should-Ignore -Path $path) {
        return
    }
    
    $relativePath = $path.Replace($WatchPath, ".")
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Detected: $changeType - $relativePath" -ForegroundColor Cyan
    
    # Schedule commit after delay
    Schedule-Commit
}

# Register events
Register-ObjectEvent -InputObject $watcher -EventName "Created" -Action $action | Out-Null
Register-ObjectEvent -InputObject $watcher -EventName "Changed" -Action $action | Out-Null
Register-ObjectEvent -InputObject $watcher -EventName "Deleted" -Action $action | Out-Null
Register-ObjectEvent -InputObject $watcher -EventName "Renamed" -Action $action | Out-Null

# Cleanup on exit
$cleanup = {
    Write-Host ""
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Stopping file watcher..." -ForegroundColor Yellow
    
    if ($script:commitTimer) {
        $script:commitTimer.Stop()
        $script:commitTimer.Dispose()
    }
    
    # Commit any pending changes before exit
    if ($script:pendingChanges) {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Commit-And-Push -Message "Auto-commit: Final changes before exit at $timestamp"
    }
    
    $watcher.EnableRaisingEvents = $false
    $watcher.Dispose()
    
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] File watcher stopped" -ForegroundColor Yellow
    exit
}

# Handle Ctrl+C
[Console]::TreatControlCAsInput = $false
$null = Register-EngineEvent PowerShell.Exiting -Action $cleanup

Write-Host "[$(Get-Date -Format 'HH:mm:ss')] File watcher is now active. Making changes will auto-commit after $CommitDelay seconds." -ForegroundColor Green
Write-Host ""

# Keep script running
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    & $cleanup
}

