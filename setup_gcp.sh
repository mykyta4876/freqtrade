#!/bin/bash
# Quick setup script for Freqtrade on GCP/Linux
# Run this after cloning the repository

set -e  # Exit on error

echo "=== Freqtrade GCP Setup Script ==="
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3.11 &> /dev/null; then
    echo "Python 3.11 not found. Installing..."
    sudo apt update
    sudo apt install -y software-properties-common
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt update
    sudo apt install -y python3.11 python3.11-venv python3.11-dev
fi

python3.11 --version
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3.11 -m venv .venv
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install freqtrade
echo "Installing freqtrade..."
pip install -e .

# Install FreqUI (optional)
echo "Installing FreqUI..."
freqtrade install-ui || echo "FreqUI installation failed (optional)"

# Create user directory
echo "Creating user directory..."
freqtrade create-userdir --userdir user_data || echo "User directory may already exist"

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source .venv/bin/activate"
echo "2. Create config: freqtrade new-config --config user_data/config.json"
echo "3. Test: freqtrade list-exchanges"
echo ""
echo "Or copy your config from Windows setup if you have one."
