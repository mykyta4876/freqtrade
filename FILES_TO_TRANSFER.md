# Files to Transfer to GCP VM

When you clone the repository on GCP, you may want to transfer these files from your Windows setup:

## Essential Files

### 1. Configuration File
**From Windows:** `user_data/config.json`  
**To GCP:** `user_data/config.json`

```bash
# Transfer command (from Windows PowerShell)
scp user_data/config.json username@vm-ip:/home/username/freqtrade/user_data/
```

### 2. Your Strategy
**From Windows:** `user_data/strategies/MyFirstStrategy.py`  
**To GCP:** `user_data/strategies/MyFirstStrategy.py`

```bash
# Transfer command (from Windows PowerShell)
scp user_data/strategies/MyFirstStrategy.py username@vm-ip:/home/username/freqtrade/user_data/strategies/
```

## Optional Files

### 3. Historical Data (if downloaded)
**From Windows:** `user_data/data/`  
**To GCP:** `user_data/data/`

```bash
# Transfer command (from Windows PowerShell)
scp -r user_data/data/ username@vm-ip:/home/username/freqtrade/user_data/
```

### 4. Backtest Results (if any)
**From Windows:** `user_data/backtest_results/`  
**To GCP:** `user_data/backtest_results/`

## What NOT to Transfer

❌ **Don't transfer:**
- `.venv/` (virtual environment - recreate on Linux)
- `__pycache__/` (Python cache)
- `*.pyc` files (compiled Python)
- `logs/` (will be recreated)

## Quick Transfer Script (Windows PowerShell)

Save this as `transfer_to_gcp.ps1`:

```powershell
# Configure these
$vmUser = "your-username"
$vmIP = "your-vm-ip"
$vmPath = "/home/$vmUser/freqtrade"

# Transfer config
scp user_data/config.json ${vmUser}@${vmIP}:${vmPath}/user_data/

# Transfer strategies
scp user_data/strategies/*.py ${vmUser}@${vmIP}:${vmPath}/user_data/strategies/

Write-Host "Transfer complete!"
```

## After Transfer

On GCP VM:

```bash
# Make sure files have correct permissions
chmod 600 user_data/config.json  # Protect config file
chmod 644 user_data/strategies/*.py

# Verify files
ls -la user_data/config.json
ls -la user_data/strategies/
```

## Alternative: Use Git

If you want to version control your config/strategies:

1. Create a private repository
2. Add `user_data/config.json` and `user_data/strategies/`
3. Clone on GCP VM
4. **Important:** Use `.gitignore` to exclude sensitive data

**⚠️ Never commit API keys to public repositories!**

## Recommended Approach

1. **On GCP VM:** Create fresh config using `freqtrade new-config`
2. **Manually copy** API keys and settings (don't transfer the file)
3. **Transfer only** your custom strategies
4. **Download data** fresh on GCP (better than transferring)

This is safer and ensures clean setup on Linux.
