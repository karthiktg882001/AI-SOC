# Script to allow network access to SOC Assistant services
# Run this script as Administrator if you can't access from other devices

Write-Host "`n🔓 Configuring Windows Firewall for SOC Assistant`n" -ForegroundColor Cyan

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "⚠️  This script requires Administrator privileges!" -ForegroundColor Yellow
    Write-Host "Please run PowerShell as Administrator and try again.`n" -ForegroundColor Yellow
    exit 1
}

# Ports to allow
$ports = @(
    @{Port=3000; Name="SOC Frontend"},
    @{Port=8000; Name="SOC ML Service"},
    @{Port=8080; Name="SOC Log Ingestion"}
)

foreach ($portConfig in $ports) {
    $port = $portConfig.Port
    $name = $portConfig.Name
    
    # Check if rule already exists
    $existingRule = Get-NetFirewallRule -DisplayName $name -ErrorAction SilentlyContinue
    
    if ($existingRule) {
        Write-Host "✓ Rule for port $port ($name) already exists" -ForegroundColor Green
    } else {
        try {
            New-NetFirewallRule -DisplayName $name -Direction Inbound -LocalPort $port -Protocol TCP -Action Allow -ErrorAction Stop
            Write-Host "✓ Created firewall rule for port $port ($name)" -ForegroundColor Green
        } catch {
            Write-Host "✗ Failed to create rule for port $port : $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

Write-Host "`n✅ Firewall configuration complete!`n" -ForegroundColor Green
Write-Host "Your SOC Assistant should now be accessible from other devices on your network." -ForegroundColor White
Write-Host "Access URL: http://192.168.0.108:3000`n" -ForegroundColor Cyan

