# Fix Windows Firewall for Freqtrade

## ✅ Confirmed: API Works in Browser

Since you can access `https://api.binance.com/api/v3/ping` in your browser and get `{}`, this confirms:
- ✅ Your internet connection works
- ✅ Binance API is accessible
- ❌ **Windows Firewall is blocking Python/aiodns**

## 🔧 Fix: Add Python to Windows Firewall

### Method 1: Through Windows Defender Firewall (Recommended)

1. **Open Windows Defender Firewall:**
   - Press `Win + R`
   - Type: `firewall.cpl`
   - Press Enter

2. **Allow Python through Firewall:**
   - Click **"Allow an app or feature through Windows Defender Firewall"** (on the left)
   - Click **"Change settings"** (top right, may need admin rights)
   - Click **"Allow another app..."** (bottom right)

3. **Add Python:**
   - Click **"Browse..."**
   - Navigate to: `C:\Users\Administrator\AppData\Local\Programs\Python\Python311\`
   - Select **`python.exe`**
   - Click **"Add"**
   - Check both **"Private"** and **"Public"** boxes
   - Click **"OK"**

4. **Also add Pythonw (if exists):**
   - Repeat steps above for `pythonw.exe` in the same folder

### Method 2: Using the Fix Script (Easiest)

1. **Right-click** on `fix_firewall.ps1` in this folder
2. Select **"Run with PowerShell"** (as Administrator)
3. Or run in PowerShell as Administrator:
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\fix_firewall.ps1
   ```

### Method 3: Through Command Line (Manual)

Run PowerShell as **Administrator** and execute:

```powershell
# Allow Python through firewall
$pythonPath = "C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe"
New-NetFirewallRule -DisplayName "Python - Freqtrade" -Direction Outbound -Program $pythonPath -Action Allow
New-NetFirewallRule -DisplayName "Python - Freqtrade Inbound" -Direction Inbound -Program $pythonPath -Action Allow
```

### Method 4: Temporarily Disable Firewall (For Testing Only)

**⚠️ Only for testing - re-enable after!**

1. Open Windows Defender Firewall
2. Click **"Turn Windows Defender Firewall on or off"** (left side)
3. Turn off for both Private and Public (temporarily)
4. Test freqtrade
5. **If it works → add Python to exceptions (Method 1)**
6. **Re-enable firewall**

## ⚠️ Important: You Need OUTBOUND Rules

**Most firewall rules are INBOUND by default, but freqtrade needs OUTBOUND rules!**

When adding Python to firewall:
- ✅ **Check OUTBOUND** (most important - for API calls)
- ✅ Check INBOUND (may be needed for some connections)

### Quick Check: Do You Have Outbound Rules?

Run in PowerShell:
```powershell
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*Python*"} | Select-Object DisplayName, Direction, Enabled
```

Look for rules with:
- `Direction = Outbound` ✅
- `Enabled = True` ✅

If you only see Inbound rules, you need to add Outbound rules!

### Complete Fix Script

I've created `fix_firewall_complete.ps1` which adds both Inbound AND Outbound rules for both venv and system Python.

**Run as Administrator:**
```powershell
powershell -ExecutionPolicy Bypass -File .\fix_firewall_complete.ps1
```

## 🧪 Test After Fixing

After adding Python to firewall, test:

```cmd
.\run_freqtrade.bat list-pairs --exchange mexc
```

Or test Binance:
```cmd
.\run_freqtrade.bat list-pairs --exchange binance
```

## 🔍 Verify MEXC API Too

Test if MEXC API works in browser:
- Open: https://api.mexc.com/api/v3/ping
- Should return: `{}`

If it works in browser but not in freqtrade → confirms firewall issue.

## 📝 Alternative: Check Antivirus

Some antivirus software also blocks network connections:

1. **Windows Defender:**
   - Open Windows Security
   - Virus & threat protection
   - Manage settings
   - Check if Python is blocked

2. **Third-party Antivirus:**
   - Check your antivirus settings
   - Add Python to exceptions/allowed programs

## ✅ Success Indicators

After fixing, you should see:
- No more `Could not contact DNS servers` errors
- `list-pairs` command works
- `download-data` command works
- Markets load successfully

## 🆘 Still Not Working?

If firewall fix doesn't work:

1. **Check if you're on corporate network:**
   - Corporate networks often block aiodns
   - Contact IT department
   - May need VPN or proxy

2. **Try different network:**
   - Mobile hotspot
   - Different WiFi
   - See if it works there

3. **Check Windows Event Viewer:**
   - Look for firewall/network blocks
   - May show what's being blocked

## 📚 Related Files

- `DNS_FIX_SUMMARY.md` - Quick DNS fix reference
- `NETWORK_TROUBLESHOOTING.md` - Detailed troubleshooting
- `MEXC_CONFIG.md` - MEXC configuration guide
