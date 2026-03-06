# MEXC Exchange Configuration

## ✅ Configuration Complete

MEXC has been configured in your `user_data/config.json`:

```json
{
    "exchange": {
        "name": "mexc",
        "key": "",
        "secret": "",
        "pair_whitelist": [
            "BTC/USDT",
            "ETH/USDT",
            "BNB/USDT"
        ]
    }
}
```

## ⚠️ DNS Issue Still Present

MEXC has the same DNS issue as Binance. The error `Could not contact DNS servers` from `aiodns` affects **all exchanges**, not just Binance.

**This is a Windows Firewall/Network issue that needs to be fixed first.**

## 🔧 Fix DNS Issue First

Before MEXC (or any exchange) will work, you need to fix the DNS issue:

### Quick Fix: Windows Firewall
1. Open **Windows Defender Firewall**
2. Click **Allow an app or feature through Windows Firewall**
3. Find **Python** and check both **Private** and **Public**
4. If Python isn't listed, click **Allow another app** and add Python
5. Try again

See `DNS_FIX_SUMMARY.md` for detailed instructions.

## 📝 MEXC Configuration Details

### Adding API Keys (When Ready)

When you're ready to trade (after fixing DNS and testing in dry-run):

1. Get API keys from MEXC:
   - Log in to MEXC
   - Go to API Management
   - Create API key with trading permissions (NOT withdrawal)

2. Update `user_data/config.json`:
```json
{
    "exchange": {
        "name": "mexc",
        "key": "your_mexc_api_key_here",
        "secret": "your_mexc_api_secret_here"
    }
}
```

### MEXC Status

- ✅ Available in CCXT (freqtrade's exchange library)
- ⚠️ Not officially supported by freqtrade team
- ✅ Should work for spot trading
- ⚠️ Use at your own discretion (may have issues)

### Testing MEXC

Once DNS is fixed, test with:

```cmd
.\run_freqtrade.bat list-pairs --exchange mexc
.\run_freqtrade.bat download-data --exchange mexc --pairs BTC/USDT --timeframes 5m --days 7
```

## 🔄 Switching Back to Binance

If you want to switch back to Binance, change in `user_data/config.json`:

```json
{
    "exchange": {
        "name": "binance",
        ...
    }
}
```

## 📚 Next Steps

1. **Fix DNS issue** (see `DNS_FIX_SUMMARY.md`)
2. **Test MEXC connection** once DNS is fixed
3. **Download data** for backtesting
4. **Test strategy** in dry-run mode
5. **Add API keys** only when ready for live trading

## ⚠️ Important Notes

- **Always start with dry-run mode** (`dry_run: true`)
- **Never share your API keys**
- **Use API keys with trading permissions only** (not withdrawal)
- **Test thoroughly before live trading**
