# Start ngrok tunnel for SOC Assistant
# This script starts ngrok and creates a public URL for your application

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SOC Assistant - ngrok Tunnel Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if ngrok exists
$ngrokPath = Join-Path $PSScriptRoot "..\ngrok.exe"
if (-not (Test-Path $ngrokPath)) {
    Write-Host "ERROR: ngrok.exe not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please download ngrok:" -ForegroundColor Yellow
    Write-Host "1. Go to https://ngrok.com/" -ForegroundColor White
    Write-Host "2. Sign up for a free account" -ForegroundColor White
    Write-Host "3. Download ngrok for Windows" -ForegroundColor White
    Write-Host "4. Place ngrok.exe in the AISOC folder" -ForegroundColor White
    Write-Host ""
    Write-Host "Or run this command to download:" -ForegroundColor Yellow
    Write-Host 'Invoke-WebRequest -Uri "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip" -OutFile "ngrok.zip"' -ForegroundColor Cyan
    Write-Host 'Expand-Archive -Path "ngrok.zip" -DestinationPath "." -Force' -ForegroundColor Cyan
    Write-Host 'Remove-Item "ngrok.zip"' -ForegroundColor Cyan
    exit 1
}

# Check if ngrok is authenticated
Write-Host "[1/3] Checking ngrok authentication..." -ForegroundColor Green
$authCheck = & $ngrokPath config check 2>&1
if ($LASTEXITCODE -ne 0 -or $authCheck -like "*not found*" -or $authCheck -like "*not authenticated*") {
    Write-Host ""
    Write-Host "ngrok is not authenticated!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To authenticate ngrok:" -ForegroundColor Yellow
    Write-Host "1. Go to https://dashboard.ngrok.com/get-started/your-authtoken" -ForegroundColor White
    Write-Host "2. Copy your authtoken" -ForegroundColor White
    Write-Host "3. Run this command:" -ForegroundColor White
    Write-Host "   .\ngrok.exe config add-authtoken YOUR_AUTHTOKEN" -ForegroundColor Cyan
    Write-Host ""
    $continue = Read-Host "Do you want to enter your authtoken now? (y/n)"
    if ($continue -eq "y" -or $continue -eq "Y") {
        $authtoken = Read-Host "Enter your ngrok authtoken"
        if ($authtoken) {
            & $ngrokPath config add-authtoken $authtoken
            if ($LASTEXITCODE -eq 0) {
                Write-Host "[OK] ngrok authenticated successfully!" -ForegroundColor Green
            } else {
                Write-Host "[FAIL] Failed to authenticate ngrok" -ForegroundColor Red
                exit 1
            }
        }
    } else {
        Write-Host "Please authenticate ngrok first, then run this script again." -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "[OK] ngrok is authenticated" -ForegroundColor Green
}

# Check if Docker is running
Write-Host ""
Write-Host "[2/3] Checking Docker services..." -ForegroundColor Green
try {
    $dockerCheck = docker ps 2>&1
    if ($LASTEXITCODE -eq 0) {
        $frontendRunning = docker-compose ps frontend 2>&1 | Select-String "Up"
        if ($frontendRunning) {
            Write-Host "[OK] Frontend service is running" -ForegroundColor Green
        } else {
            Write-Host "[WARN] Frontend service may not be running" -ForegroundColor Yellow
            Write-Host "Starting services..." -ForegroundColor Yellow
            docker-compose up -d
            Start-Sleep -Seconds 5
        }
    } else {
        Write-Host "[FAIL] Docker is not running" -ForegroundColor Red
        Write-Host "Please start Docker Desktop" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "[FAIL] Docker not found" -ForegroundColor Red
    exit 1
}

# Start ngrok tunnel
Write-Host ""
Write-Host "[3/3] Starting ngrok tunnel..." -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ngrok Tunnel Active" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your application is now accessible at:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Look for the 'Forwarding' line above" -ForegroundColor White
Write-Host "Example: https://abc123.ngrok-free.app -> http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Share the HTTPS URL with your friend!" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the tunnel" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start ngrok
& $ngrokPath http 3000

