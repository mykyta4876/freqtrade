# Complete Firewall Fix for Freqtrade
# Run this script as Administrator

Write-Host "=== Freqtrade Firewall Fix ===" -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

# Python paths
$venvPython = "D:\Project\freqtrade-develop\.venv\Scripts\python.exe"
$systemPython = "C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe"

# Check if paths exist
$pathsToAdd = @()
if (Test-Path $venvPython) {
    $pathsToAdd += $venvPython
    Write-Host "✓ Found venv Python: $venvPython" -ForegroundColor Green
} else {
    Write-Host "✗ Venv Python not found: $venvPython" -ForegroundColor Yellow
}

if (Test-Path $systemPython) {
    $pathsToAdd += $systemPython
    Write-Host "✓ Found system Python: $systemPython" -ForegroundColor Green
} else {
    Write-Host "✗ System Python not found: $systemPython" -ForegroundColor Yellow
}

if ($pathsToAdd.Count -eq 0) {
    Write-Host "ERROR: No Python executables found!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Removing old Python firewall rules..." -ForegroundColor Yellow
Remove-NetFirewallRule -DisplayName "Python - Freqtrade*" -ErrorAction SilentlyContinue
Remove-NetFirewallRule -DisplayName "Freqtrade*" -ErrorAction SilentlyContinue

# Add firewall rules for each Python
foreach ($pythonPath in $pathsToAdd) {
    $pythonName = Split-Path $pythonPath -Leaf
    Write-Host ""
    Write-Host "Adding firewall rules for: $pythonName" -ForegroundColor Cyan
    
    # Outbound rule (most important for API calls)
    try {
        New-NetFirewallRule -DisplayName "Python - Freqtrade Outbound ($pythonName)" `
            -Direction Outbound `
            -Program $pythonPath `
            -Action Allow `
            -Profile Any `
            -ErrorAction Stop
        Write-Host "  ✓ Outbound rule added" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Failed to add outbound rule: $_" -ForegroundColor Red
    }
    
    # Inbound rule (may be needed for some connections)
    try {
        New-NetFirewallRule -DisplayName "Python - Freqtrade Inbound ($pythonName)" `
            -Direction Inbound `
            -Program $pythonPath `
            -Action Allow `
            -Profile Any `
            -ErrorAction Stop
        Write-Host "  ✓ Inbound rule added" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Failed to add inbound rule: $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=== Firewall Rules Added ===" -ForegroundColor Green
Write-Host ""
Write-Host "Current Python firewall rules:" -ForegroundColor Cyan
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*Freqtrade*"} | 
    Select-Object DisplayName, Direction, Enabled | Format-Table -AutoSize

Write-Host ""
Write-Host "✅ Firewall configuration complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Now test freqtrade:" -ForegroundColor Cyan
Write-Host "  .\run_freqtrade.bat list-pairs --exchange mexc" -ForegroundColor White
Write-Host ""
Write-Host "If it still doesn't work:" -ForegroundColor Yellow
Write-Host "  1. Check Windows Defender (may also block connections)" -ForegroundColor White
Write-Host "  2. Try temporarily disabling firewall to test" -ForegroundColor White
Write-Host "  3. Check if you're on a corporate network" -ForegroundColor White
