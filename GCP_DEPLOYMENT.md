# Freqtrade Deployment on GCP VM (Linux)

## Quick Setup Guide

### 1. Create GCP VM

1. Go to Google Cloud Console
2. Create a new VM instance:
   - **OS**: Ubuntu 22.04 LTS or Debian 11+ (recommended)
   - **Machine type**: e2-medium or higher (2 vCPU, 4GB RAM minimum)
   - **Boot disk**: 20GB+ SSD
   - **Firewall**: Allow HTTP/HTTPS traffic
   - **SSH access**: Enable

### 2. Connect to VM

```bash
# From your local machine
gcloud compute ssh your-vm-name --zone=your-zone

# Or use SSH key
ssh -i ~/.ssh/gcp_key username@vm-external-ip
```

### 3. Clone and Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip git

# Clone your repository
git clone https://github.com/freqtrade/freqtrade.git
# Or if you have your own fork:
# git clone https://github.com/your-username/freqtrade.git

cd freqtrade

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install freqtrade
pip install -e .

# Install FreqUI (optional)
freqtrade install-ui
```

### 4. Configure Freqtrade

```bash
# Create user directory
freqtrade create-userdir --userdir user_data

# Create config (interactive)
freqtrade new-config --config user_data/config.json

# Or copy your existing config
# (if you have config.json from Windows setup)
```

### 5. Configure MEXC (or your exchange)

Edit `user_data/config.json`:

```json
{
    "exchange": {
        "name": "mexc",
        "key": "your_api_key",
        "secret": "your_api_secret",
        "pair_whitelist": [
            "BTC/USDT",
            "ETH/USDT"
        ]
    },
    "dry_run": true,
    "stake_currency": "USDT",
    "stake_amount": 30
}
```

### 6. Test Connection

```bash
# List pairs (tests exchange connection)
freqtrade list-pairs --exchange mexc

# Download data
freqtrade download-data --exchange mexc --pairs BTC/USDT --timeframes 5m --days 30

# List strategies
freqtrade list-strategies
```

### 7. Run in Dry-Run Mode

```bash
# Start trading bot (dry-run)
freqtrade trade --config user_data/config.json --strategy MyFirstStrategy
```

### 8. Run as Service (Optional - for 24/7 operation)

Create systemd service:

```bash
sudo nano /etc/systemd/system/freqtrade.service
```

Add:

```ini
[Unit]
Description=Freqtrade Trading Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/freqtrade
Environment="PATH=/home/your-username/freqtrade/.venv/bin"
ExecStart=/home/your-username/freqtrade/.venv/bin/freqtrade trade --config user_data/config.json --strategy MyFirstStrategy
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable freqtrade
sudo systemctl start freqtrade
sudo systemctl status freqtrade
```

### 9. Web UI (Optional)

```bash
# Start web server
freqtrade webserver --config user_data/config.json

# Access via: http://your-vm-external-ip:8080
# Make sure to configure firewall rules in GCP to allow port 8080
```

### 10. Monitor Logs

```bash
# View logs
tail -f user_data/logs/freqtrade.log

# Or if running as service
sudo journalctl -u freqtrade -f
```

## Important Notes

### Security

1. **API Keys**: Never commit API keys to git
2. **Firewall**: Only open necessary ports
3. **SSH**: Use key-based authentication
4. **Updates**: Keep system and freqtrade updated

### Files to Transfer from Windows

If you want to keep your Windows setup:

1. **Config file**: `user_data/config.json`
2. **Strategies**: `user_data/strategies/MyFirstStrategy.py`
3. **Data** (optional): `user_data/data/` (if you have downloaded data)

Transfer using:
```bash
# From Windows (PowerShell)
scp user_data/config.json username@vm-ip:/home/username/freqtrade/user_data/
scp user_data/strategies/*.py username@vm-ip:/home/username/freqtrade/user_data/strategies/
```

### Advantages of GCP VM

✅ No Windows aiodns issues  
✅ Better network connectivity  
✅ Can run 24/7  
✅ More stable  
✅ Better performance  
✅ Easy to scale  

### Cost Estimate

- **e2-medium**: ~$25-30/month
- **e2-small**: ~$12-15/month (minimum, may be slow)
- **Free tier**: e2-micro (not recommended for trading bot)

## Quick Commands Reference

```bash
# Activate venv
source .venv/bin/activate

# Update freqtrade
git pull
pip install -r requirements.txt
pip install -e .

# Backtest
freqtrade backtesting --config user_data/config.json --strategy MyFirstStrategy

# Download data
freqtrade download-data --exchange mexc --pairs BTC/USDT --timeframes 5m --days 30

# Start trading
freqtrade trade --config user_data/config.json --strategy MyFirstStrategy

# Web UI
freqtrade webserver --config user_data/config.json
```

## Troubleshooting

### If you get permission errors:
```bash
sudo chown -R $USER:$USER ~/freqtrade
```

### If Python version is wrong:
```bash
# Check version
python3 --version

# Install specific version
sudo apt install python3.11 python3.11-venv
```

### If port 8080 is blocked:
```bash
# Check firewall
sudo ufw status

# Allow port (if using ufw)
sudo ufw allow 8080/tcp
```

## Next Steps After Setup

1. ✅ Test connection to exchange
2. ✅ Download historical data
3. ✅ Backtest your strategy
4. ✅ Run in dry-run mode
5. ✅ Monitor for a few days
6. ✅ Only then consider live trading

Good luck with your GCP deployment! 🚀
