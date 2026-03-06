#!/bin/bash
# Quick setup script for GCP VM
# Run this ON the GCP VM after connecting via SSH

set -e

echo "=== Freqtrade GCP VM Setup ==="

# Update system
echo "Updating system..."
sudo apt-get update && sudo apt-get upgrade -y

# Install Python and dependencies
echo "Installing Python and dependencies..."
sudo apt-get install -y python3.11 python3.11-venv python3-pip git build-essential wget

# Install TA-Lib
echo "Installing TA-Lib..."
if [ ! -f /usr/lib/libta_lib.a ]; then
    wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
    tar -xzf ta-lib-0.4.0-src.tar.gz
    cd ta-lib/
    ./configure --prefix=/usr
    make
    sudo make install
    cd ..
    rm -rf ta-lib ta-lib-0.4.0-src.tar.gz
fi

# Clone freqtrade if not exists
if [ ! -d "freqtrade" ]; then
    echo "Cloning freqtrade..."
    git clone https://github.com/freqtrade/freqtrade.git
    cd freqtrade
    git checkout develop
else
    echo "Freqtrade directory exists, skipping clone..."
    cd freqtrade
fi

# Create virtual environment
echo "Creating virtual environment..."
python3.11 -m venv .venv
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install freqtrade
echo "Installing freqtrade..."
pip install -e .

# Create user_data directories
echo "Creating user_data directories..."
mkdir -p user_data/strategies
mkdir -p user_data/data
mkdir -p user_data/logs

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "Next steps:"
echo "1. Transfer your config.json and strategies from Windows"
echo "2. Activate venv: source .venv/bin/activate"
echo "3. Test: freqtrade list-strategies"
echo "4. Download data: freqtrade download-data --exchange mexc --pairs BTC/USDT --timeframes 5m --days 30"
echo "5. Run: freqtrade trade --config user_data/config.json --strategy MyFirstStrategy"
