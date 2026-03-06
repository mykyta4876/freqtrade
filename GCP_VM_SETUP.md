# Freqtrade Setup on GCP VM

## Why GCP VM?

GCP VMs don't have the Windows DNS/network blocking issues. This is a common and recommended way to run trading bots.

## Prerequisites

- GCP account with billing enabled
- Basic Linux knowledge (or follow commands)

## Step 1: Create GCP VM

### Via GCP Console:

1. Go to [GCP Console](https://console.cloud.google.com/)
2. Navigate to **Compute Engine** → **VM instances**
3. Click **Create Instance**
4. Configure:
   - **Name**: `freqtrade-bot`
   - **Machine type**: `e2-small` or `e2-medium` (2GB RAM minimum)
   - **Boot disk**: Ubuntu 22.04 LTS (20GB minimum)
   - **Firewall**: Allow HTTP and HTTPS traffic
5. Click **Create**

### Via gcloud CLI:

```bash
gcloud compute instances create freqtrade-bot \
    --zone=us-central1-a \
    --machine-type=e2-small \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=20GB
```

## Step 2: Connect to VM

### Via SSH in Browser:
- Click **SSH** button next to your VM instance

### Via gcloud CLI:
```bash
gcloud compute ssh freqtrade-bot --zone=us-central1-a
```

## Step 3: Install Dependencies

Once connected to VM, run:

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Python 3.11+ and dependencies
sudo apt-get install -y python3.11 python3.11-venv python3-pip git

# Install TA-Lib dependencies
sudo apt-get install -y build-essential wget
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
cd ..
rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# Install Python TA-Lib
pip3 install TA-Lib
```

## Step 4: Clone/Transfer Freqtrade

### Option A: Clone from GitHub (Recommended)

```bash
# Clone freqtrade
git clone https://github.com/freqtrade/freqtrade.git
cd freqtrade
git checkout develop
```

### Option B: Transfer Your Local Project

From your Windows machine, use SCP or upload via GCP Console:

```powershell
# From Windows PowerShell
gcloud compute scp --recurse D:\Project\freqtrade-develop freqtrade-bot:~/freqtrade --zone=us-central1-a
```

Or use `rsync` if you have it:
```bash
# From Windows (if you have WSL or rsync)
rsync -avz -e "gcloud compute ssh --zone=us-central1-a" D:\Project\freqtrade-develop/ freqtrade-bot:~/freqtrade/
```

## Step 5: Install Freqtrade

```bash
cd ~/freqtrade  # or wherever you cloned/transferred it

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install freqtrade
pip install -e .
```

## Step 6: Transfer Your Configuration

### Transfer config and strategy files:

From Windows:
```powershell
# Transfer config
gcloud compute scp user_data/config.json freqtrade-bot:~/freqtrade/user_data/ --zone=us-central1-a

# Transfer strategy
gcloud compute scp --recurse user_data/strategies freqtrade-bot:~/freqtrade/user_data/ --zone=us-central1-a
```

Or manually create on VM:
```bash
# On VM, create config
mkdir -p ~/freqtrade/user_data/strategies
nano ~/freqtrade/user_data/config.json
# Paste your config (or use the one below)
```

### Basic Config for GCP VM:

```json
{
    "$schema": "https://schema.freqtrade.io/schema.json",
    "max_open_trades": 3,
    "stake_currency": "USDT",
    "stake_amount": 30,
    "timeframe": "5m",
    "dry_run": true,
    "dry_run_wallet": 1000,
    "exchange": {
        "name": "mexc",
        "key": "",
        "secret": "",
        "pair_whitelist": [
            "BTC/USDT",
            "ETH/USDT"
        ]
    },
    "pairlists": [
        {"method": "StaticPairList"}
    ],
    "stoploss": -0.10,
    "minimal_roi": {
        "40": 0.0,
        "30": 0.01,
        "20": 0.02,
        "0": 0.04
    }
}
```

## Step 7: Test Freqtrade

```bash
# Activate venv
source .venv/bin/activate

# Test
freqtrade list-strategies
freqtrade list-pairs --exchange mexc

# Download data
freqtrade download-data --exchange mexc --pairs BTC/USDT --timeframes 5m --days 30
```

## Step 8: Run Freqtrade

### Interactive Mode:
```bash
source .venv/bin/activate
freqtrade trade --config user_data/config.json --strategy MyFirstStrategy
```

### Background Mode (screen):
```bash
screen -S freqtrade
source .venv/bin/activate
freqtrade trade --config user_data/config.json --strategy MyFirstStrategy
# Press Ctrl+A then D to detach
```

### Systemd Service (Recommended for Production):

Create service file:
```bash
sudo nano /etc/systemd/system/freqtrade.service
```

Paste:
```ini
[Unit]
Description=Freqtrade Trading Bot
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/freqtrade
Environment="PATH=/home/YOUR_USERNAME/freqtrade/.venv/bin"
ExecStart=/home/YOUR_USERNAME/freqtrade/.venv/bin/freqtrade trade --config user_data/config.json --strategy MyFirstStrategy
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

## Step 9: Web UI (Optional)

```bash
# Install FreqUI
freqtrade install-ui

# Start web server
freqtrade webserver --config user_data/config.json
```

Access via: `http://YOUR_VM_EXTERNAL_IP:8080`

**Important**: Add firewall rule in GCP to allow port 8080:
```bash
gcloud compute firewall-rules create allow-freqtrade-ui \
    --allow tcp:8080 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow Freqtrade UI"
```

## Step 10: Security (Important!)

### Add API Keys Securely:

```bash
# Edit config
nano user_data/config.json

# Or use environment variables (more secure)
export FREQTRADE__EXCHANGE__KEY="your_key"
export FREQTRADE__EXCHANGE__SECRET="your_secret"
```

### Firewall Rules:
- Only allow necessary ports (22 for SSH, 8080 for UI if needed)
- Use GCP firewall rules, not just VM firewall

### SSH Keys:
- Use SSH keys instead of passwords
- Disable password authentication

## Useful Commands

```bash
# View logs
journalctl -u freqtrade -f  # if using systemd
# or
tail -f ~/freqtrade/user_data/logs/freqtrade.log

# Stop bot
sudo systemctl stop freqtrade  # if using systemd
# or Ctrl+C if running interactively

# Check status
freqtrade show-trades
freqtrade status
```

## Cost Estimate

- **e2-small**: ~$6-10/month
- **e2-medium**: ~$12-20/month
- **Storage**: ~$2/month for 20GB

**Free tier**: GCP gives $300 credit for new accounts!

## Troubleshooting

### If freqtrade command not found:
```bash
source .venv/bin/activate
```

### If TA-Lib fails:
```bash
# Make sure you installed system TA-Lib first (Step 3)
sudo apt-get install -y libta-lib0.4.0
```

### Check disk space:
```bash
df -h
```

### Check memory:
```bash
free -h
```

## Next Steps

1. ✅ Set up VM and install freqtrade
2. ✅ Transfer your config and strategy
3. ✅ Test in dry-run mode
4. ✅ Download historical data
5. ✅ Backtest your strategy
6. ✅ Run in dry-run mode for a few days
7. ⚠️ Only then consider live trading

## Resources

- GCP Documentation: https://cloud.google.com/compute/docs
- Freqtrade Docs: https://www.freqtrade.io
- Your local files are ready to transfer!

Good luck with your trading bot! 🚀
