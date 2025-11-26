# PowerShell script to start ngrok using Docker (no local installation needed)

Write-Host "🚀 Starting Ngrok Tunnel using Docker..." -ForegroundColor Green
Write-Host ""

# Check if Docker is running
try {
    docker ps | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check if services are running
Write-Host ""
Write-Host "🔍 Checking if services are running..." -ForegroundColor Cyan
$frontendRunning = docker ps --filter "name=aisoc-frontend" --format "{{.Names}}" 2>&1
if ($frontendRunning -match "aisoc-frontend") {
    Write-Host "✅ Frontend container is running" -ForegroundColor Green
} else {
    Write-Host "⚠️  Frontend container not running. Starting services..." -ForegroundColor Yellow
    docker compose up -d
    Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
}

# Authtoken is already configured
$authtoken = "2lKJLvVJ5YeWq3tpskEQRuQGos1_35ja74h4maKCsk4FKefzb"

Write-Host ""
Write-Host "🌐 Starting ngrok tunnel on port 3000..." -ForegroundColor Cyan
Write-Host "   Web interface: http://localhost:4040" -ForegroundColor Gray
Write-Host "   Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

docker run -it --rm `
    -p 4040:4040 `
    --network aisoc_soc-network `
    -e NGROK_AUTHTOKEN=$authtoken `
    ngrok/ngrok http host.docker.internal:3000

