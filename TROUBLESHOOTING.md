# Troubleshooting Guide

## File Lock Error During Installation

If you encounter `[WinError 32] The process cannot access the file because it is being used by another process` when trying to install freqtrade, here are solutions:

### Solution 1: Use PYTHONPATH (Recommended Workaround)

You can use freqtrade without installing it by setting PYTHONPATH:

**PowerShell:**
```powershell
$env:PYTHONPATH = "$PWD;$env:PYTHONPATH"
python -m freqtrade --version
```

**Or use the helper script:**
```powershell
.\run_freqtrade.ps1 --version
```

**To make it permanent in your current session:**
```powershell
$env:PYTHONPATH = "D:\Project\freqtrade-develop;$env:PYTHONPATH"
```

### Solution 2: Fix File Lock Issue

The file lock is usually caused by:

1. **Windows Defender / Antivirus**
   - Add the project folder to exclusions
   - Temporarily disable real-time protection during installation

2. **File Indexing Service**
   - Disable Windows Search indexing for this folder
   - Or wait a few minutes and try again

3. **IDE/Editor (Cursor/VS Code)**
   - Close the IDE temporarily
   - Or exclude `freqtrade.egg-info` from file watching

4. **Other Python Processes**
   - Close any other Python processes
   - Check Task Manager for python.exe processes

### Solution 3: Clean Install

```powershell
# Remove build artifacts
Remove-Item -Recurse -Force freqtrade.egg-info -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue

# Close all Python processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Wait a few seconds
Start-Sleep -Seconds 3

# Try installing again
pip install -e .
```

### Solution 4: Install in Different Location

If the file lock persists, you can:
1. Copy the project to a different location
2. Install from there
3. Or use PYTHONPATH method (Solution 1)

## Using Freqtrade Without Installation

Since all dependencies are installed, you can use freqtrade directly:

**Option 1: Using Batch File (Recommended - No Execution Policy Issues)**
```cmd
.\run_freqtrade.bat trade --config user_data/config.json --strategy MyFirstStrategy
.\run_freqtrade.bat list-strategies
.\run_freqtrade.bat download-data --exchange binance --pairs BTC/USDT --timeframes 5m --days 30
```

Or in Command Prompt (cmd.exe):
```cmd
run_freqtrade.bat trade --config user_data/config.json --strategy MyFirstStrategy
```

**Option 2: Manual PYTHONPATH (PowerShell)**
```powershell
# Set PYTHONPATH (do this each time you open a new terminal)
$env:PYTHONPATH = "D:\Project\freqtrade-develop;$env:PYTHONPATH"

# Run freqtrade
python -m freqtrade trade --config user_data/config.json --strategy MyFirstStrategy
```

**Option 3: Using PowerShell Script (If Execution Policy is Set)**
```powershell
powershell -ExecutionPolicy Bypass -File .\run_freqtrade.ps1 trade --config user_data/config.json --strategy MyFirstStrategy
```

## Verify Installation

Check if freqtrade works:
```powershell
$env:PYTHONPATH = "$PWD;$env:PYTHONPATH"
python -m freqtrade --version
python -m freqtrade list-exchanges
```

## Common Issues

### "Module not found" errors
- Make sure virtual environment is activated: `.venv\Scripts\Activate.ps1`
- Make sure PYTHONPATH is set if not installed

### TA-Lib errors
- TA-Lib requires additional setup on Windows
- See: https://www.freqtrade.io/en/stable/installation/#ta-lib

### Permission errors
- Run PowerShell as Administrator
- Check folder permissions

## Need More Help?

- Documentation: https://www.freqtrade.io
- Discord: https://discord.gg/p7nuUNVfP7
- GitHub Issues: https://github.com/freqtrade/freqtrade/issues
