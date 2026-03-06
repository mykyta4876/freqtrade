# Quick Start Guide - Freqtrade Trading Bot

## 🚀 Installation (Choose One Method)

### Method 1: Automated Setup (Recommended)

**If you get an execution policy error**, run PowerShell as Administrator and use:
```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

Or temporarily change policy:
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.\setup.ps1
```

Select option **A** (requirements.txt) when prompted.

**See `INSTALL_WINDOWS.md` for detailed Windows installation help.**

### Method 2: Manual Installation (No Script Needed)
```powershell
# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Install freqtrade (if you get file lock errors, see Method 3)
pip install -e .

# Install FreqUI (optional)
freqtrade install-ui
```

### Method 3: Use Without Installation (If Installation Fails)
If you encounter file lock errors during installation, you can use freqtrade directly:

**Option A: Using Batch File (No Execution Policy Issues)**
```cmd
.\run_freqtrade.bat list-strategies
.\run_freqtrade.bat trade --config user_data/config.json --strategy MyFirstStrategy
```

Or in Command Prompt (cmd.exe):
```cmd
run_freqtrade.bat list-strategies
run_freqtrade.bat trade --config user_data/config.json --strategy MyFirstStrategy
```

**Option B: Manual Setup (PowerShell)**
```powershell
# Activate virtual environment
.venv\Scripts\Activate.ps1

# Set PYTHONPATH (do this each time you open a new terminal)
$env:PYTHONPATH = "$PWD;$env:PYTHONPATH"

# Run freqtrade
python -m freqtrade list-strategies
```

**Option C: Using PowerShell Script (Requires Execution Policy)**
If you've set execution policy, you can use:
```powershell
powershell -ExecutionPolicy Bypass -File .\run_freqtrade.ps1 list-strategies
```

**See `TROUBLESHOOTING.md` for detailed help with installation issues.**

## ⚙️ Configuration

1. **Edit your config file**: `user_data/config.json`
   - Set your exchange API keys (or leave empty for dry-run)
   - Adjust stake amount, max trades, etc.

2. **Your strategy is ready**: `user_data/strategies/MyFirstStrategy.py`
   - Simple RSI-based strategy
   - Entry: RSI crosses above 30
   - Exit: RSI crosses above 70

## 📊 Download Historical Data

**Using batch file:**
```cmd
.\run_freqtrade.bat download-data --exchange binance --pairs BTC/USDT ETH/USDT --timeframes 5m --days 30
```

**Or manually:**
```powershell
$env:PYTHONPATH = "$PWD;$env:PYTHONPATH"
python -m freqtrade download-data --exchange binance --pairs BTC/USDT ETH/USDT --timeframes 5m --days 30
```

## 🧪 Backtest Your Strategy

**Using batch file:**
```cmd
.\run_freqtrade.bat backtesting --config user_data/config.json --strategy MyFirstStrategy --timerange 20240101-20240131
```

**Or manually:**
```powershell
$env:PYTHONPATH = "$PWD;$env:PYTHONPATH"
python -m freqtrade backtesting --config user_data/config.json --strategy MyFirstStrategy --timerange 20240101-20240131
```

## ▶️ Start Trading (Dry-Run Mode)

**Using batch file:**
```cmd
.\run_freqtrade.bat trade --config user_data/config.json --strategy MyFirstStrategy
```

**Or manually:**
```powershell
$env:PYTHONPATH = "$PWD;$env:PYTHONPATH"
python -m freqtrade trade --config user_data/config.json --strategy MyFirstStrategy
```

## 🌐 Web Interface

Start the web server:
```cmd
.\run_freqtrade.bat webserver --config user_data/config.json
```

**Or manually:**
```powershell
$env:PYTHONPATH = "$PWD;$env:PYTHONPATH"
python -m freqtrade webserver --config user_data/config.json
```

Open: http://localhost:8080
- Username: `freqtrader`
- Password: `SuperSecurePassword` (change this in config.json!)

## 📝 Next Steps

1. **Test in dry-run mode** - Never start with real money!
2. **Backtest thoroughly** - Test your strategy with historical data
3. **Optimize parameters** - Use `freqtrade hyperopt` to find best settings
4. **Customize strategy** - Edit `MyFirstStrategy.py` to add your own logic
5. **Read documentation** - Check `GETTING_STARTED.md` for detailed info

## ⚠️ Important Warnings

- **Always start with `dry_run: true`**
- **Never risk money you can't afford to lose**
- **Test thoroughly before live trading**
- **Understand your strategy before deploying**

## 📚 Resources

- Windows Installation Help: `INSTALL_WINDOWS.md`
- Troubleshooting: `TROUBLESHOOTING.md`
- Full Guide: `GETTING_STARTED.md`
- Documentation: https://www.freqtrade.io
- Discord: https://discord.gg/p7nuUNVfP7

Happy Trading! 🎉
