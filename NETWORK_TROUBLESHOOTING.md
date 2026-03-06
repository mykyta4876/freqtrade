# Network Troubleshooting Guide

## ⚠️ DNS Error: "Could not contact DNS servers"

**This is a Windows network/firewall configuration issue, not a freqtrade bug.**

The error occurs because `aiodns` (async DNS library) cannot contact DNS servers on your system, even though Windows DNS works fine. This is typically caused by firewall or network policy restrictions.

If you see errors like:
- `Could not contact DNS servers`
- `Cannot connect to host api.binance.com:443`
- `ClientConnectorDNSError`

This is a network connectivity issue. Here are solutions:

## Solution 1: Use System DNS Instead of aiodns

The issue might be with the `aiodns` library. Try disabling it by setting an environment variable:

**PowerShell:**
```powershell
$env:CCXT_DISABLE_AIOHTTP_DNS = "1"
.\run_freqtrade.bat download-data --exchange binance --pairs BTC/USDT --timeframes 5m --days 30
```

**Command Prompt:**
```cmd
set CCXT_DISABLE_AIOHTTP_DNS=1
run_freqtrade.bat download-data --exchange binance --pairs BTC/USDT --timeframes 5m --days 30
```

## Solution 2: Check Internet Connection

Test if you can reach Binance:
```cmd
ping api.binance.com
```

If ping fails, check:
- Internet connection
- Firewall settings
- VPN/Proxy configuration

## Solution 3: Flush DNS Cache

Clear Windows DNS cache:
```cmd
ipconfig /flushdns
```

Then try again.

## Solution 4: Use Different DNS Servers

Temporarily use Google DNS:
1. Open Network Settings
2. Change DNS to: 8.8.8.8 and 8.8.4.4
3. Try again

## Solution 5: Check Firewall/Antivirus

- Temporarily disable Windows Firewall
- Check if antivirus is blocking connections
- Add freqtrade/python to firewall exceptions

## Solution 6: Use Proxy (If Behind Corporate Firewall)

If you're behind a corporate firewall, configure proxy in config.json:

```json
{
    "exchange": {
        "name": "binance",
        "ccxt_config": {
            "aiohttp_trust_env": true
        },
        "ccxt_async_config": {
            "aiohttp_trust_env": true
        }
    }
}
```

Set proxy environment variables:
```cmd
set HTTP_PROXY=http://proxy.example.com:8080
set HTTPS_PROXY=http://proxy.example.com:8080
```

## Solution 7: Test with Different Exchange

Try a different exchange to see if it's Binance-specific:
```cmd
.\run_freqtrade.bat download-data --exchange kraken --pairs BTC/USD --timeframes 5m --days 7
```

## Solution 8: Use Synchronous Mode

If async DNS continues to fail, you can try using the synchronous CCXT client (though this is slower):

Edit your config.json and add:
```json
{
    "exchange": {
        "name": "binance",
        "ccxt_config": {
            "enableRateLimit": true
        }
    }
}
```

## Quick Test Commands

1. **Test DNS resolution:**
   ```cmd
   nslookup api.binance.com
   ```

2. **Test HTTPS connection:**
   ```cmd
   curl https://api.binance.com/api/v3/ping
   ```

3. **Check if Python can resolve DNS:**
   ```cmd
   python -c "import socket; print(socket.gethostbyname('api.binance.com'))"
   ```

## Root Cause

The error `Could not contact DNS servers` from `aiodns` indicates that:
- ✅ System DNS works fine (ping works, browser works)
- ❌ But `aiodns` (async DNS library used by aiohttp/ccxt) cannot contact DNS servers
- 🔒 This is almost always a **Windows Firewall or network policy issue**

**Why this happens:**
- `aiodns` uses a different method to query DNS than Windows system DNS
- Windows Firewall or network policies may block `aiodns` specifically
- Corporate networks often restrict async DNS queries

## Most Likely Solutions

### Solution 1: Check Windows Firewall
Windows Firewall might be blocking aiodns from accessing DNS:

1. Open Windows Defender Firewall
2. Check if Python or aiodns is blocked
3. Temporarily disable firewall to test
4. If it works, add Python to firewall exceptions

### Solution 2: Network Policy / Corporate Firewall
If you're on a corporate network:
- Contact IT to allow aiodns DNS queries
- Or use a VPN
- Or configure proxy settings

### Solution 3: Use Different Network
Try:
- Different WiFi network
- Mobile hotspot
- Different location

### Solution 4: Wait and Retry
Sometimes this is a temporary network glitch:
- Wait 5-10 minutes
- Try again
- Check if Binance API is accessible in browser: https://api.binance.com/api/v3/ping

### Solution 5: Use Manual Data Import
If download continues to fail, you can:
- Download data manually from Binance
- Import using freqtrade's data conversion tools
- Or use a different data source

## Still Having Issues?

**This is a network/DNS configuration issue, not a freqtrade bug.**

1. **Verify Binance API is accessible:**
   - Open browser: https://api.binance.com/api/v3/ping
   - Should return: `{}`

2. **Check Windows Firewall:**
   - Temporarily disable to test
   - If it works, add Python to exceptions

3. **Try different network:**
   - Mobile hotspot
   - Different WiFi
   - VPN

4. **Check if you're behind corporate firewall:**
   - Contact IT department
   - Configure proxy if needed

5. **Alternative: Use manual data:**
   - Download CSV from Binance
   - Convert using freqtrade tools
   - Or use a different exchange that works

6. **Check freqtrade logs:** `user_data/logs/`

**Note:** This is a known issue on some Windows systems where aiodns cannot contact DNS servers even though system DNS works. The workaround is usually firewall/network configuration.
