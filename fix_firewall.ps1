# Fix Windows Firewall for Freqtrade
# Run this script as Administrator

$pythonPath = "C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe"

Write-Host "Adding Python to Windows Firewall..." -ForegroundColor Green

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

# Check if Python exists
if (-not (Test-Path $pythonPath)) {
    Write-Host "ERROR: Python not found at: $pythonPath" -ForegroundColor Red
    Write-Host "Please update the path in this script" -ForegroundColor Yellow
    exit 1
}

# Remove existing rules (if any)
Write-Host "Removing existing Python firewall rules..." -ForegroundColor Yellow
Remove-NetFirewallRule -DisplayName "Python - Freqtrade" -ErrorAction SilentlyContinue

# Add outbound rule
Write-Host "Adding outbound rule..." -ForegroundColor Yellow
New-NetFirewallRule -DisplayName "Python - Freqtrade" `
    -Direction Outbound `
    -Program $pythonPath `
    -Action Allow `
    -Profile Any `
    -ErrorAction Stop

# Add inbound rule (may be needed for some connections)
Write-Host "Adding inbound rule..." -ForegroundColor Yellow
New-NetFirewallRule -DisplayName "Python - Freqtrade Inbound" `
    -Direction Inbound `
    -Program $pythonPath `
    -Action Allow `
    -Profile Any `
    -ErrorAction Stop

Write-Host "`n✅ Success! Python has been added to Windows Firewall" -ForegroundColor Green
Write-Host "`nNow test freqtrade:" -ForegroundColor Cyan
Write-Host "  .\run_freqtrade.bat list-pairs --exchange mexc" -ForegroundColor White
