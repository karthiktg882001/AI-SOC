# SOC Assistant - Remote Access Setup Script
# This script helps configure your system for remote access

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SOC Assistant - Remote Access Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script requires Administrator privileges!" -ForegroundColor Red
    Write-Host "Please run PowerShell as Administrator and try again." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Right-click PowerShell -> Run as Administrator" -ForegroundColor Yellow
    exit 1
}

Write-Host "[1/5] Getting network information..." -ForegroundColor Green

# Get local IP address
$localIPs = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { 
    $_.IPAddress -notlike "127.*" -and 
    $_.IPAddress -notlike "169.254.*" -and
    $_.InterfaceAlias -notlike "*Loopback*"
} | Select-Object IPAddress, InterfaceAlias

Write-Host ""
Write-Host "Local IP Addresses:" -ForegroundColor Yellow
$localIPs | ForEach-Object {
    Write-Host "  - $($_.IPAddress) ($($_.InterfaceAlias))" -ForegroundColor White
}

$primaryIP = ($localIPs | Select-Object -First 1).IPAddress

# Get public IP
Write-Host ""
Write-Host "[2/5] Getting public IP address..." -ForegroundColor Green
try {
    $publicIP = (Invoke-WebRequest -Uri "https://api.ipify.org" -UseBasicParsing -TimeoutSec 5).Content
    Write-Host "Public IP: $publicIP" -ForegroundColor Yellow
} catch {
    Write-Host "Could not retrieve public IP (check internet connection)" -ForegroundColor Red
    $publicIP = "Unable to retrieve"
}

Write-Host ""
Write-Host "[3/5] Configuring Windows Firewall..." -ForegroundColor Green

# Check if rules already exist
$existingRules = Get-NetFirewallRule -DisplayName "SOC Assistant*" -ErrorAction SilentlyContinue

if ($existingRules) {
    Write-Host "Firewall rules already exist. Removing old rules..." -ForegroundColor Yellow
    Remove-NetFirewallRule -DisplayName "SOC Assistant*" -ErrorAction SilentlyContinue
}

# Create firewall rules
$ports = @(
    @{Port=3000; Name="Frontend"},
    @{Port=8000; Name="ML Service"},
    @{Port=8080; Name="Log Ingestion"}
)

foreach ($port in $ports) {
    try {
        New-NetFirewallRule -DisplayName "SOC Assistant $($port.Name)" `
            -Direction Inbound `
            -LocalPort $port.Port `
            -Protocol TCP `
            -Action Allow `
            -Description "Allow SOC Assistant $($port.Name) on port $($port.Port)" | Out-Null
        Write-Host "  [OK] Allowed port $($port.Port) ($($port.Name))" -ForegroundColor Green
    } catch {
        Write-Host "  [FAIL] Failed to allow port $($port.Port)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "[4/5] Checking Docker services..." -ForegroundColor Green

# Check if Docker is running
try {
    $dockerRunning = docker ps 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Docker is running" -ForegroundColor Green
        
        # Check if containers are running
        $containers = docker-compose ps 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [OK] Docker Compose is available" -ForegroundColor Green
        } else {
            Write-Host "  [WARN] Docker Compose not found or services not running" -ForegroundColor Yellow
            Write-Host "    Run: docker-compose up -d" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  [FAIL] Docker is not running" -ForegroundColor Red
        Write-Host "    Please start Docker Desktop" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  [FAIL] Docker not found" -ForegroundColor Red
    Write-Host "    Please install Docker Desktop" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[5/5] Setup Summary" -ForegroundColor Green
Write-Host "==================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Local Network Access:" -ForegroundColor Yellow
Write-Host "  URL: http://$primaryIP:3000" -ForegroundColor White
Write-Host ""
Write-Host "Public IP (for port forwarding):" -ForegroundColor Yellow
Write-Host "  IP: $publicIP" -ForegroundColor White
Write-Host "  URL: http://$publicIP:3000" -ForegroundColor White
Write-Host ""
Write-Host "Firewall Rules:" -ForegroundColor Yellow
Write-Host "  [OK] Port 3000 (Frontend)" -ForegroundColor Green
Write-Host "  [OK] Port 8000 (ML Service)" -ForegroundColor Green
Write-Host "  [OK] Port 8080 (Log Ingestion)" -ForegroundColor Green
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "===========" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Same Network Access:" -ForegroundColor Yellow
Write-Host "   Share this URL with friends on your network:" -ForegroundColor White
Write-Host "   http://$primaryIP:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Internet Access (Port Forwarding):" -ForegroundColor Yellow
Write-Host "   a. Log into your router admin panel" -ForegroundColor White
Write-Host "   b. Forward ports 3000, 8000, 8080 to $primaryIP" -ForegroundColor White
Write-Host "   c. Share: http://$publicIP:3000" -ForegroundColor White
Write-Host ""
Write-Host "3. Internet Access (ngrok - Temporary):" -ForegroundColor Yellow
Write-Host "   a. Install ngrok from https://ngrok.com/" -ForegroundColor White
Write-Host "   b. Run: ngrok http 3000" -ForegroundColor White
Write-Host "   c. Share the ngrok HTTPS URL" -ForegroundColor White
Write-Host ""
Write-Host "4. Security:" -ForegroundColor Yellow
Write-Host "   [WARN] Change default passwords!" -ForegroundColor Red
Write-Host "   [WARN] Use HTTPS for internet access!" -ForegroundColor Red
Write-Host "   [WARN] Consider VPN for better security!" -ForegroundColor Red
Write-Host ""

Write-Host "For detailed instructions, see: REMOTE_ACCESS_GUIDE.md" -ForegroundColor Cyan
Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green

