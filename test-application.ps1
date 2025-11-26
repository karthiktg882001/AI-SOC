# Comprehensive Testing Script for AI SOC Assistant
# Tests all major features and endpoints

Write-Host "🧪 AI SOC Assistant - Comprehensive Testing" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Colors
$success = "Green"
$errorColor = "Red"
$info = "Cyan"
$warning = "Yellow"

# Test Results
$testResults = @()

function Test-Service {
    param(
        [string]$ServiceName,
        [string]$Url,
        [string]$ExpectedStatus = "200"
    )
    
    Write-Host "Testing $ServiceName..." -ForegroundColor $info -NoNewline
    try {
        $response = Invoke-WebRequest -Uri $Url -Method Get -TimeoutSec 5 -ErrorAction Stop
        if ($response.StatusCode -eq $ExpectedStatus) {
            Write-Host " ✅ PASS" -ForegroundColor $success
            $script:testResults += @{Service = $ServiceName; Status = "PASS"; Details = "Status: $($response.StatusCode)" }
            return $true
        }
        else {
            Write-Host " ⚠️  WARNING (Status: $($response.StatusCode))" -ForegroundColor $warning
            $script:testResults += @{Service = $ServiceName; Status = "WARNING"; Details = "Status: $($response.StatusCode)" }
            return $false
        }
    }
    catch {
        Write-Host " ❌ FAIL" -ForegroundColor $errorColor
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor $errorColor
        $script:testResults += @{Service = $ServiceName; Status = "FAIL"; Details = $_.Exception.Message }
        return $false
    }
}

function Test-APIEndpoint {
    param(
        [string]$EndpointName,
        [string]$Url,
        [hashtable]$Headers = @{},
        [string]$Method = "GET"
    )
    
    Write-Host "  Testing $EndpointName..." -ForegroundColor Gray -NoNewline
    try {
        $params = @{
            Uri         = $Url
            Method      = $Method
            Headers     = $Headers
            TimeoutSec  = 5
            ErrorAction = "Stop"
        }
        
        $response = Invoke-RestMethod @params
        Write-Host " ✅" -ForegroundColor $success
        $script:testResults += @{Service = $EndpointName; Status = "PASS"; Details = "OK" }
        return $true
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        if ($statusCode -eq 401 -or $statusCode -eq 403) {
            Write-Host " ⚠️  (Auth Required)" -ForegroundColor $warning
            $script:testResults += @{Service = $EndpointName; Status = "AUTH_REQUIRED"; Details = "Status: $statusCode" }
            return $true  # Auth required is expected for protected endpoints
        }
        else {
            Write-Host " ❌" -ForegroundColor $errorColor
            $script:testResults += @{Service = $EndpointName; Status = "FAIL"; Details = "Status: $statusCode" }
            return $false
        }
    }
}

# Check Docker Services
Write-Host "📦 Checking Docker Services..." -ForegroundColor $info
Write-Host ""

$services = @(
    @{Name = "Frontend"; Container = "aisoc-frontend-1"; Port = 3000 },
    @{Name = "ML Service"; Container = "aisoc-ml-service-1"; Port = 8000 },
    @{Name = "Log Ingestion"; Container = "aisoc-log-ingestion-service-1"; Port = 8080 },
    @{Name = "PostgreSQL"; Container = "aisoc-postgres-1"; Port = 5432 },
    @{Name = "MongoDB"; Container = "aisoc-mongodb-1"; Port = 27017 },
    @{Name = "Kafka"; Container = "aisoc-kafka-1"; Port = 9092 },
    @{Name = "Neo4j"; Container = "aisoc-neo4j-1"; Port = 7474 },
    @{Name = "Automation Service"; Container = "aisoc-automation-service-1"; Port = 8001 }
)

$allServicesRunning = $true
foreach ($service in $services) {
    $containerStatus = docker ps --filter "name=$($service.Container)" --format "{{.Status}}" 2>&1
    if ($containerStatus -match "Up") {
        Write-Host "  ✅ $($service.Name) - Running" -ForegroundColor $success
    }
    else {
        Write-Host "  ❌ $($service.Name) - Not Running" -ForegroundColor $errorColor
        $allServicesRunning = $false
    }
}

Write-Host ""

if (-not $allServicesRunning) {
    Write-Host "⚠️  Some services are not running. Starting services..." -ForegroundColor $warning
    docker compose up -d
    Write-Host "⏳ Waiting for services to start..." -ForegroundColor $info
    Start-Sleep -Seconds 10
}

# Test Service Health
Write-Host ""
Write-Host "🏥 Testing Service Health Endpoints..." -ForegroundColor $info
Write-Host ""

Test-Service -ServiceName "ML Service Health" -Url "http://localhost:8000/health"
Test-Service -ServiceName "Frontend" -Url "http://localhost:3000"

# Test API Endpoints
Write-Host ""
Write-Host "🔌 Testing API Endpoints..." -ForegroundColor $info
Write-Host ""

# Public endpoints (no auth required)
Test-APIEndpoint -EndpointName "Root" -Url "http://localhost:8000/"
Test-APIEndpoint -EndpointName "Health" -Url "http://localhost:8000/health"

# Protected endpoints (auth required - should return 401/403)
Write-Host ""
Write-Host "🔐 Testing Protected Endpoints (Auth Required)..." -ForegroundColor $info
Write-Host ""

Test-APIEndpoint -EndpointName "Dashboard Stats" -Url "http://localhost:8000/api/dashboard/stats"
Test-APIEndpoint -EndpointName "Recent Threats" -Url "http://localhost:8000/api/threats/recent"
Test-APIEndpoint -EndpointName "Incidents" -Url "http://localhost:8000/api/incidents"
Test-APIEndpoint -EndpointName "User Profile" -Url "http://localhost:8000/api/auth/me"

# Test Login Endpoint
Write-Host ""
Write-Host "🔑 Testing Authentication..." -ForegroundColor $info
Write-Host ""

Write-Host "  Testing Login Endpoint..." -ForegroundColor Gray -NoNewline
try {
    $loginData = @{
        username = "admin@soc.local"
        password = "Admin@12345"
    } | ConvertTo-Json
    
    $params = @{
        Uri         = "http://localhost:8000/api/auth/login"
        Method      = "POST"
        ContentType = "application/x-www-form-urlencoded"
        Body        = "username=admin@soc.local&password=Admin@12345"
        TimeoutSec  = 10
        ErrorAction = "Stop"
    }
    
    $loginResponse = Invoke-RestMethod @params
    if ($loginResponse.access_token) {
        Write-Host " ✅ Login Successful" -ForegroundColor $success
        $global:authToken = $loginResponse.access_token
        $script:testResults += @{Service = "Login"; Status = "PASS"; Details = "Token received" }
        
        # Test authenticated endpoints
        Write-Host ""
        Write-Host "🔓 Testing Authenticated Endpoints..." -ForegroundColor $info
        Write-Host ""
        
        $authHeaders = @{
            "Authorization" = "Bearer $global:authToken"
        }
        
        Test-APIEndpoint -EndpointName "Dashboard Stats (Auth)" -Url "http://localhost:8000/api/dashboard/stats" -Headers $authHeaders
        Test-APIEndpoint -EndpointName "Recent Threats (Auth)" -Url "http://localhost:8000/api/threats/recent?limit=10" -Headers $authHeaders
        Test-APIEndpoint -EndpointName "User Profile (Auth)" -Url "http://localhost:8000/api/auth/me" -Headers $authHeaders
        Test-APIEndpoint -EndpointName "Incidents (Auth)" -Url "http://localhost:8000/api/incidents" -Headers $authHeaders
        
    }
    else {
        Write-Host " ⚠️  Login response missing token" -ForegroundColor $warning
        $script:testResults += @{Service = "Login"; Status = "WARNING"; Details = "No token in response" }
    }
}
catch {
    Write-Host " ❌ Login Failed" -ForegroundColor $errorColor
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor $errorColor
    $script:testResults += @{Service = "Login"; Status = "FAIL"; Details = $_.Exception.Message }
}

# Test Frontend Access
Write-Host ""
Write-Host "🌐 Testing Frontend Access..." -ForegroundColor $info
Write-Host ""

try {
    $frontendResponse = Invoke-WebRequest -Uri "http://localhost:3000" -Method Get -TimeoutSec 5
    if ($frontendResponse.StatusCode -eq 200) {
        Write-Host "  ✅ Frontend accessible" -ForegroundColor $success
        $script:testResults += @{Service = "Frontend Access"; Status = "PASS"; Details = "Status: 200" }
    }
}
catch {
    Write-Host "  ❌ Frontend not accessible" -ForegroundColor $errorColor
    $script:testResults += @{Service = "Frontend Access"; Status = "FAIL"; Details = $_.Exception.Message }
}

# Summary
Write-Host ""
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "📊 Test Summary" -ForegroundColor $info
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$passed = ($testResults | Where-Object { $_.Status -eq "PASS" }).Count
$failed = ($testResults | Where-Object { $_.Status -eq "FAIL" }).Count
$warnings = ($testResults | Where-Object { $_.Status -eq "WARNING" -or $_.Status -eq "AUTH_REQUIRED" }).Count
$total = $testResults.Count

Write-Host "Total Tests: $total" -ForegroundColor White
Write-Host "✅ Passed: $passed" -ForegroundColor $success
Write-Host "⚠️  Warnings: $warnings" -ForegroundColor $warning
Write-Host "❌ Failed: $failed" -ForegroundColor $errorColor
Write-Host ""

if ($failed -eq 0) {
    Write-Host "🎉 All critical tests passed!" -ForegroundColor $success
}
else {
    Write-Host "⚠️  Some tests failed. Check the details above." -ForegroundColor $warning
}

Write-Host ""
Write-Host "🌐 Access Points:" -ForegroundColor $info
Write-Host "   • Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   • ML Service API: http://localhost:8000" -ForegroundColor White
Write-Host "   • API Docs: http://localhost:8000/docs" -ForegroundColor White
if ($global:authToken) {
    Write-Host ""
    Write-Host "🔑 Authentication Token:" -ForegroundColor $info
    Write-Host "   Token: $($global:authToken.Substring(0, 20))..." -ForegroundColor Gray
    Write-Host "   Use this token for API testing:" -ForegroundColor Gray
    Write-Host "   Authorization: Bearer $global:authToken" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor $info
Write-Host "   1. Open http://localhost:3000 in your browser" -ForegroundColor White
Write-Host "   2. Login with: admin@soc.local / Admin@12345" -ForegroundColor White
Write-Host "   3. Test all features in the UI" -ForegroundColor White
Write-Host "   4. Check API documentation at http://localhost:8000/docs" -ForegroundColor White
Write-Host ""

