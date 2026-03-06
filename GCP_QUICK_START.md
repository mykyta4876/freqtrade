# GCP VM Quick Start - Freqtrade

## 🚀 5-Minute Setup

```bash
# 1. Connect to your GCP VM
gcloud compute ssh your-vm-name --zone=your-zone

# 2. Clone repository
git clone https://github.com/freqtrade/freqtrade.git
cd freqtrade

# 3. Run setup script
chmod +x setup_gcp.sh
./setup_gcp.sh

# 4. Activate virtual environment
source .venv/bin/activate

# 5. Create config
freqtrade new-config --config user_data/config.json

# 6. Test connection
freqtrade list-pairs --exchange mexc
```

## ⚙️ Configure MEXC

Edit `user_data/config.json` and set:
- Exchange: `"mexc"`
- API keys (when ready)
- Strategy: `"MyFirstStrategy"`

## 📊 Download Data

```bash
freqtrade download-data --exchange mexc --pairs BTC/USDT --timeframes 5m --days 30
```

## 🧪 Backtest

```bash
freqtrade backtesting --config user_data/config.json --strategy MyFirstStrategy
```

## ▶️ Start Trading (Dry-Run)

```bash
freqtrade trade --config user_data/config.json --strategy MyFirstStrategy
```

## 🌐 Web UI

```bash
freqtrade webserver --config user_data/config.json
# Access: http://your-vm-ip:8080
```

## 📝 Transfer Files from Windows (Optional)

If you want to keep your Windows config/strategies:

```bash
# From Windows PowerShell
scp user_data/config.json username@vm-ip:/home/username/freqtrade/user_data/
scp user_data/strategies/MyFirstStrategy.py username@vm-ip:/home/username/freqtrade/user_data/strategies/
```

## ✅ Advantages of GCP

- ✅ No Windows aiodns issues
- ✅ Better network connectivity  
- ✅ Runs 24/7
- ✅ More stable
- ✅ Better performance

## 📚 Full Guide

See `GCP_DEPLOYMENT.md` for detailed instructions.
