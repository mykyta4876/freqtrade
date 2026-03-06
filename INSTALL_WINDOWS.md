# Windows Installation Guide - Freqtrade

## PowerShell Execution Policy Issue

If you see an error about execution policy, you have several options:

### Option 1: Bypass Execution Policy (Recommended for One-Time Use)

Run PowerShell as Administrator and execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.\setup.ps1
```

Or run the script directly with bypass:
```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

### Option 2: Change Execution Policy (Permanent)

Run PowerShell as Administrator:
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then run:
```powershell
.\setup.ps1
```

### Option 3: Manual Installation (No Script Needed)

Follow these steps manually:

#### Step 1: Create Virtual Environment
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

#### Step 2: Upgrade pip
```powershell
python -m pip install --upgrade pip
```

#### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

#### Step 4: Install Freqtrade
```powershell
pip install -e .
```

#### Step 5: Install FreqUI (Optional)
```powershell
freqtrade install-ui
```

#### Step 6: Verify Installation
```powershell
freqtrade --version
```

## After Installation

1. **Activate virtual environment** (always do this before using freqtrade):
   ```powershell
   .venv\Scripts\Activate.ps1
   ```

2. **Create user directory** (if not already done):
   ```powershell
   freqtrade create-userdir --userdir user_data
   ```

3. **Start using freqtrade** - See `QUICK_START.md` for next steps!

## Troubleshooting

### If you get "python: command not found"
- Make sure Python is in your PATH
- Or use full path: `C:\Python311\python.exe` (adjust version/path as needed)

### If you get module errors
- Make sure virtual environment is activated
- Reinstall: `pip install -r requirements.txt`

### If TA-Lib installation fails
TA-Lib requires additional setup on Windows. See: https://www.freqtrade.io/en/stable/installation/#ta-lib

## Quick Test

After installation, test with:
```powershell
freqtrade list-exchanges
```

This should show a list of supported exchanges.
