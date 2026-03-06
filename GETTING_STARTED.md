# Getting Started with Freqtrade Trading Bot

This guide will help you set up and run your freqtrade trading bot.

## Prerequisites

- ✅ Python 3.11+ (You have Python 3.11.4 installed)
- Git (for cloning the repository)
- A crypto exchange account (Binance, Kraken, Bybit, etc.)

## Step 1: Install Freqtrade

### Option A: Using the Setup Script (Recommended for Windows)

Run the PowerShell setup script:

```powershell
.\setup.ps1
```

This script will:
- Create a virtual environment
- Install all required dependencies
- Install freqtrade in development mode
- Install FreqUI (web interface)

### Option B: Manual Installation

1. Create a virtual environment:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install dependencies:
```powershell
pip install -r requirements.txt
pip install -e .
```

3. Install FreqUI (optional):
```powershell
freqtrade install-ui
```

## Step 2: Initialize Configuration

1. Create user directory structure:
```powershell
freqtrade create-userdir --userdir user_data
```

2. Create a new configuration file:
```powershell
freqtrade new-config --config user_data/config.json
```

This will ask you questions about:
- Dry-run mode (recommended: Yes for testing)
- Stake currency (e.g., USDT, BTC)
- Stake amount per trade
- Maximum open trades
- Timeframe (e.g., 5m, 15m, 1h)
- Exchange selection
- Telegram setup (optional)

## Step 3: Configure Exchange API Keys

Edit `user_data/config.json` and add your exchange API credentials:

```json
{
    "exchange": {
        "name": "binance",
        "key": "your_api_key_here",
        "secret": "your_api_secret_here",
        "ccxt_config": {},
        "ccxt_async_config": {}
    }
}
```

⚠️ **Important**: 
- Start with `dry_run: true` to test without real money
- Never share your API keys
- Use API keys with only trading permissions (not withdrawal)

## Step 4: Create Your First Strategy

Create a new strategy:

```powershell
freqtrade new-strategy --strategy MyFirstStrategy --template full
```

This creates `user_data/strategies/MyFirstStrategy.py` with example indicators and entry/exit logic.

## Step 5: Download Historical Data

Download data for backtesting:

```powershell
freqtrade download-data --exchange binance --pairs BTC/USDT ETH/USDT --timeframes 5m 1h --days 30
```

## Step 6: Backtest Your Strategy

Test your strategy with historical data:

```powershell
freqtrade backtesting --config user_data/config.json --strategy MyFirstStrategy --timerange 20240101-20240131
```

## Step 7: Run in Dry-Run Mode

Start the bot in dry-run mode (simulated trading):

```powershell
freqtrade trade --config user_data/config.json --strategy MyFirstStrategy
```

## Step 8: Monitor Your Bot

### Web UI (FreqUI)
Start the web server:
```powershell
freqtrade webserver --config user_data/config.json
```

Then open: http://localhost:8080

### Telegram (Optional)
Configure Telegram in `config.json` to receive notifications and control the bot remotely.

## Common Commands

- **List strategies**: `freqtrade list-strategies`
- **List pairs**: `freqtrade list-pairs --exchange binance`
- **Show trades**: `freqtrade show-trades`
- **Plot profit**: `freqtrade plot-profit --config user_data/config.json`

## Next Steps

1. **Learn Strategy Development**: Read `docs/strategy-customization.md`
2. **Optimize Parameters**: Use `freqtrade hyperopt` to find optimal parameters
3. **Use FreqAI**: Advanced machine learning strategies (optional)
4. **Join Community**: Discord: https://discord.gg/p7nuUNVfP7

## Important Warnings

⚠️ **Always start with dry-run mode**
⚠️ **Never risk money you can't afford to lose**
⚠️ **Test thoroughly before live trading**
⚠️ **Understand your strategy before deploying**

## Resources

- Documentation: https://www.freqtrade.io
- Strategy Repository: https://github.com/freqtrade/freqtrade-strategies
- Discord Community: https://discord.gg/p7nuUNVfP7

Happy Trading! 🚀
