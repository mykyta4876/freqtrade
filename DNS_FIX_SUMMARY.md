# DNS Issue - Quick Summary

## The Problem
You're seeing: `aiodns.error.DNSError: (11, 'Could not contact DNS servers')`

This means:
- ✅ Your internet connection works (ping works)
- ✅ Windows DNS works fine
- ❌ But `aiodns` (used by freqtrade) cannot reach DNS servers
- 🔒 **This is a Windows Firewall/Network Policy issue**

## Quick Fixes (Try in Order)

### 1. Check Windows Firewall ⭐ (Most Common Fix)
1. Open **Windows Defender Firewall**
2. Click **Allow an app or feature through Windows Firewall**
3. Find **Python** and check both **Private** and **Public**
4. If Python isn't listed, click **Allow another app** and add Python
5. Try freqtrade again

**Or temporarily disable firewall to test:**
- If it works with firewall off → add Python to exceptions
- If it still fails → try next solution

### 2. Test Binance API Access
Open in browser: https://api.binance.com/api/v3/ping
- Should return: `{}`
- If it fails → network/proxy issue

### 3. Try Different Network
- Mobile hotspot
- Different WiFi
- VPN
- If it works → your network is blocking aiodns

### 4. Corporate Network?
If you're on a corporate/enterprise network:
- Contact IT department
- Ask them to allow `aiodns` DNS queries
- Or configure proxy settings

### 5. Flush DNS Cache
```cmd
ipconfig /flushdns
```
Then try again.

## Workarounds (If Fixes Don't Work)

### Option A: Use Manual Data
- Download data from Binance manually
- Import using freqtrade conversion tools
- See: https://www.freqtrade.io/en/stable/data-download/

### Option B: Try Different Exchange
Some exchanges might work:
```cmd
.\run_freqtrade.bat download-data --exchange kraken --pairs BTC/USD --timeframes 5m --days 7
```

### Option C: Use Existing Data
If you have any historical data files, you can use those for backtesting without downloading.

## Why Code Fixes Don't Work

We've tried several code-level fixes, but they don't work because:
- `aiodns` is deeply integrated into `aiohttp`/`ccxt`
- It's initialized before we can patch it
- The issue is at the network/firewall level, not code level

## Need More Help?

- Full troubleshooting: See `NETWORK_TROUBLESHOOTING.md`
- Freqtrade Discord: https://discord.gg/p7nuUNVfP7
- GitHub Issues: https://github.com/freqtrade/freqtrade/issues

**Most users fix this by adding Python to Windows Firewall exceptions.**
