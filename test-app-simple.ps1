# Simple Testing Script for AI SOC Assistant
Write-Host "=== AI SOC Assistant Testing ===" -ForegroundColor Green
Write-Host ""

# Test Services
Write-Host "1. Checking Docker Services..." -ForegroundColor Cyan
docker compose ps --format "table {{.Name}}\t{{.Status}}"
Write-Host ""

# Test Health Endpoints
Write-Host "2. Testing Health Endpoints..." -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
    Write-Host "   ML Service Health: OK" -ForegroundColor Green
    Write-Host "   Status: $($health.status)" -ForegroundColor Gray
} catch {
    Write-Host "   ML Service Health: FAILED" -ForegroundColor Red
}

try {
    $frontend = Invoke-WebRequest -Uri "http://localhost:3000" -Method Get -TimeoutSec 5
    Write-Host "   Frontend: OK (Status: $($frontend.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "   Frontend: FAILED" -ForegroundColor Red
}
Write-Host ""

# Test Login
Write-Host "3. Testing Authentication..." -ForegroundColor Cyan
try {
    $body = "username=admin@soc.local&password=Admin@12345"
    $login = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" `
        -Method POST -ContentType "application/x-www-form-urlencoded" -Body $body
    
    if ($login.access_token) {
        Write-Host "   Login: SUCCESS" -ForegroundColor Green
        $global:token = $login.access_token
        Write-Host "   Token received: $($token.Substring(0, 20))..." -ForegroundColor Gray
        
        # Test authenticated endpoint
        Write-Host ""
        Write-Host "4. Testing Authenticated Endpoints..." -ForegroundColor Cyan
        $headers = @{ "Authorization" = "Bearer $token" }
        
        try {
            $stats = Invoke-RestMethod -Uri "http://localhost:8000/api/dashboard/stats" -Headers $headers
            Write-Host "   Dashboard Stats: OK" -ForegroundColor Green
        } catch {
            Write-Host "   Dashboard Stats: FAILED" -ForegroundColor Red
        }
        
        try {
            $threats = Invoke-RestMethod -Uri "http://localhost:8000/api/threats/recent?limit=5" -Headers $headers
            Write-Host "   Recent Threats: OK" -ForegroundColor Green
        } catch {
            Write-Host "   Recent Threats: FAILED" -ForegroundColor Red
        }
    } else {
        Write-Host "   Login: FAILED (No token)" -ForegroundColor Red
    }
} catch {
    Write-Host "   Login: FAILED" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Summary
Write-Host "=== Test Summary ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access Points:" -ForegroundColor Yellow
Write-Host "  - Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "  - ML Service API: http://localhost:8000" -ForegroundColor White
Write-Host "  - API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Test Credentials:" -ForegroundColor Yellow
Write-Host "  - Email: admin@soc.local" -ForegroundColor White
Write-Host "  - Password: Admin@12345" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Open http://localhost:3000 in your browser" -ForegroundColor White
Write-Host "  2. Login and test all features" -ForegroundColor White
Write-Host "  3. Check API documentation at http://localhost:8000/docs" -ForegroundColor White
Write-Host ""

