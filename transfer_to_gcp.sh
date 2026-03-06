#!/bin/bash
# Script to transfer freqtrade files to GCP VM
# Run from your local machine (if you have bash/WSL) or adapt for Windows

VM_NAME="freqtrade-bot"
ZONE="us-central1-a"  # Change to your zone
PROJECT_DIR="D:/Project/freqtrade-develop"  # Windows path

echo "Transferring freqtrade to GCP VM..."

# Transfer config
echo "Transferring config.json..."
gcloud compute scp "$PROJECT_DIR/user_data/config.json" \
    $VM_NAME:~/freqtrade/user_data/ --zone=$ZONE

# Transfer strategies
echo "Transferring strategies..."
gcloud compute scp --recurse "$PROJECT_DIR/user_data/strategies" \
    $VM_NAME:~/freqtrade/user_data/ --zone=$ZONE

echo "Transfer complete!"
echo "Now SSH to VM and run: cd ~/freqtrade && source .venv/bin/activate"
