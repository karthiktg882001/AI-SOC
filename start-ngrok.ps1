# PowerShell script to start ngrok for AI SOC Project

Write-Host "🚀 Starting Ngrok Tunnel for AI SOC Project..." -ForegroundColor Green
Write-Host ""

# Check if ngrok is installed
try {
    $ngrokVersion = ngrok version 2>&1
    Write-Host "✅ Ngrok found: $ngrokVersion" -ForegroundColor Green
}
catch {
    Write-Host "❌ Ngrok not found. Please install ngrok first." -ForegroundColor Red
    Write-Host "   Download from: https://ngrok.com/download" -ForegroundColor Yellow
    Write-Host "   Or use: choco install ngrok" -ForegroundColor Yellow
    exit 1
}

# Check if Docker containers are running
Write-Host ""
Write-Host "🔍 Checking Docker containers..." -ForegroundColor Cyan
$frontendRunning = docker ps --filter "name=aisoc-frontend" --format "{{.Names}}" 2>&1
if ($frontendRunning -match "aisoc-frontend") {
    Write-Host "✅ Frontend container is running" -ForegroundColor Green
}
else {
    Write-Host "⚠️  Frontend container not running. Starting services..." -ForegroundColor Yellow
    docker compose up -d
    Start-Sleep -Seconds 5
}

# Check if port 3000 is accessible
Write-Host ""
Write-Host "🌐 Starting ngrok tunnel on port 3000..." -ForegroundColor Cyan
Write-Host "   This will expose your frontend (which proxies to ML service)" -ForegroundColor Gray
Write-Host ""
Write-Host "📝 Note: You'll need to set your ngrok authtoken first:" -ForegroundColor Yellow
Write-Host "   ngrok config add-authtoken YOUR_TOKEN" -ForegroundColor Yellow
Write-Host ""
Write-Host "🔗 After starting, visit http://localhost:4040 for ngrok web interface" -ForegroundColor Cyan
Write-Host ""

# Start ngrok
ngrok http 3000

