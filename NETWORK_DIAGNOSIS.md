# Network Diagnosis - aiodns Issue

## Current Status

✅ System DNS works (`socket.gethostbyname` works)  
✅ Browser can access APIs  
✅ Firewall OUTBOUND rules added  
✅ Windows Defender disabled  
❌ **aiodns still fails: "Could not contact DNS servers"**

## Root Cause Analysis

Since everything else works but aiodns fails, this indicates:

1. **Network-level blocking** - Your network/router/ISP is blocking aiodns DNS queries
2. **Windows DNS client issue** - aiodns uses Windows DNS APIs differently than system DNS
3. **Corporate network policy** - If on corporate network, IT may have blocked async DNS

## Tests Performed

- ✅ System DNS: `socket.gethostbyname('api.mexc.com')` → Works
- ✅ Browser: `https://api.binance.com/api/v3/ping` → Works  
- ❌ aiodns: Direct test → Fails with "Could not contact DNS servers"
- ✅ Firewall: OUTBOUND rules added
- ✅ Windows Defender: Disabled

## Solutions to Try

### 1. Test on Different Network (Most Important)

**This will tell us if it's your network or the system:**

- Connect to **mobile hotspot**
- Try freqtrade again
- **If it works → Your network/ISP is blocking aiodns**
- **If it still fails → System-level issue**

### 2. Check if Corporate Network

If you're on a corporate/enterprise network:

- Contact IT department
- Ask them to allow `aiodns` DNS queries
- Or ask for VPN access
- Corporate networks often block async DNS for security

### 3. Check Router/Network Settings

Your router might be blocking async DNS:

- Log into router admin panel
- Check DNS settings
- Try changing DNS to Google DNS (8.8.8.8, 8.8.4.4)
- Or Cloudflare DNS (1.1.1.1, 1.0.0.1)

### 4. Try VPN

If network is blocking aiodns:

- Use a VPN
- Test freqtrade through VPN
- If it works → Network is blocking aiodns

### 5. Check Windows DNS Client Service

```cmd
sc query Dnscache
```

Make sure DNS Client service is running.

### 6. Flush and Reset DNS

```cmd
ipconfig /flushdns
ipconfig /release
ipconfig /renew
```

### 7. Check for Proxy

If you're behind a proxy:

- Check proxy settings: `netsh winhttp show proxy`
- Configure proxy in freqtrade config if needed

## Most Likely Cause

Based on the symptoms:
- **Network-level blocking** (ISP/router/corporate firewall)
- **Corporate network policy** blocking async DNS

## Next Steps

1. **Test on mobile hotspot** (most important test)
2. **Check if corporate network** (contact IT if yes)
3. **Try VPN** (if available)
4. **Check router DNS settings**

## Workaround: Use Manual Data

If network blocking cannot be resolved:

- Download data manually from exchange websites
- Import using freqtrade conversion tools
- Use for backtesting without live API access

## Why This Happens

`aiodns` uses Windows DNS APIs in a way that some networks block:
- Async DNS queries look suspicious to firewalls
- Corporate networks often block for security
- Some ISPs block non-standard DNS methods

System DNS works because it uses standard Windows DNS client, but aiodns uses lower-level APIs that get blocked.
