# PowerShell script to test all SOC services
# Run: .\scripts\test_all_services.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SOC Assistant - Service Health Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost"
$allServicesOk = $true

# Test Frontend
Write-Host "Testing Frontend (Port 3000)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl:3000" -Method Get -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ Frontend is running" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Frontend is not accessible: $($_.Exception.Message)" -ForegroundColor Red
    $allServicesOk = $false
}

# Test ML Service
Write-Host "Testing ML Service (Port 8000)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl:8000/health" -Method Get -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        $content = $response.Content | ConvertFrom-Json
        Write-Host "✓ ML Service is running" -ForegroundColor Green
        Write-Host "  Status: $($content.status)" -ForegroundColor Gray
    }
} catch {
    Write-Host "✗ ML Service is not accessible: $($_.Exception.Message)" -ForegroundColor Red
    $allServicesOk = $false
}

# Test Log Ingestion Service
Write-Host "Testing Log Ingestion Service (Port 8080)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl:8080/api/logs/stats" -Method Get -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ Log Ingestion Service is running" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Log Ingestion Service is not accessible: $($_.Exception.Message)" -ForegroundColor Red
    $allServicesOk = $false
}

# Test ML Service API Endpoints
Write-Host "Testing ML Service API Endpoints..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl:8000/api/dashboard/stats" -Method Get -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ Dashboard API is working" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Dashboard API failed: $($_.Exception.Message)" -ForegroundColor Red
    $allServicesOk = $false
}

# Get Docker Container Status
Write-Host ""
Write-Host "Checking Docker Containers..." -ForegroundColor Yellow
try {
    $containers = docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host $containers
    } else {
        Write-Host "✗ Could not check Docker containers" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Docker command failed" -ForegroundColor Red
}

# Get Network IP (for mobile testing)
Write-Host ""
Write-Host "Network Information for Mobile Testing:" -ForegroundColor Yellow
try {
    $ipConfig = ipconfig | Select-String "IPv4" | Select-Object -First 1
    if ($ipConfig) {
        $ip = ($ipConfig -split ":")[1].Trim()
        Write-Host "Your IP Address: $ip" -ForegroundColor Cyan
        Write-Host "Access from mobile: http://$ip:3000" -ForegroundColor Cyan
    }
} catch {
    Write-Host "Could not determine IP address" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
if ($allServicesOk) {
    Write-Host "✓ All services are running correctly!" -ForegroundColor Green
} else {
    Write-Host "✗ Some services have issues. Check logs above." -ForegroundColor Red
}
Write-Host "========================================" -ForegroundColor Cyan

