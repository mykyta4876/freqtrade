import logging
from pathlib import Path

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse
from starlette.responses import FileResponse


logger = logging.getLogger(__name__)

router_ui = APIRouter(include_in_schema=False, tags=["Web UI"])


@router_ui.get("/favicon.ico")
async def favicon():
    return FileResponse(str(Path(__file__).parent / "ui/favicon.ico"))


@router_ui.get("/fallback_file.html")
async def fallback():
    return FileResponse(str(Path(__file__).parent / "ui/fallback_file.html"))


@router_ui.get("/ui_version")
async def ui_version():
    from freqtrade.commands.deploy_ui import read_ui_version

    uibase = Path(__file__).parent / "ui/installed/"
    version = read_ui_version(uibase)

    return {
        "version": version if version else "not_installed",
    }


@router_ui.get("/check-data", response_class=HTMLResponse)
async def check_data_page():
    """
    Serve a simple HTML page for checking data completeness.
    """
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Freqtrade Data Check</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #1a1a1a;
            color: #e0e0e0;
            padding: 20px;
            line-height: 1.6;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            color: #4CAF50;
            margin-bottom: 30px;
            text-align: center;
        }
        .form-group {
            background: #2a2a2a;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #b0b0b0;
            font-weight: 500;
        }
        input, select {
            width: 100%;
            padding: 10px;
            background: #1a1a1a;
            border: 1px solid #444;
            border-radius: 4px;
            color: #e0e0e0;
            font-size: 14px;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #4CAF50;
        }
        button {
            background: #4CAF50;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 500;
            width: 100%;
            margin-top: 10px;
        }
        button:hover {
            background: #45a049;
        }
        button:disabled {
            background: #666;
            cursor: not-allowed;
        }
        .results {
            margin-top: 30px;
            display: none;
        }
        .results.show {
            display: block;
        }
        .status-card {
            background: #2a2a2a;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .status-complete {
            border-left: 4px solid #4CAF50;
        }
        .status-incomplete {
            border-left: 4px solid #ff9800;
        }
        .status-empty {
            border-left: 4px solid #f44336;
        }
        .stat {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #333;
        }
        .stat:last-child {
            border-bottom: none;
        }
        .stat-label {
            color: #b0b0b0;
        }
        .stat-value {
            color: #e0e0e0;
            font-weight: 500;
        }
        .gaps {
            margin-top: 20px;
        }
        .gap-item {
            background: #1a1a1a;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 10px;
            border-left: 3px solid #ff9800;
        }
        .gap-item strong {
            color: #ff9800;
        }
        .loading {
            text-align: center;
            padding: 20px;
            color: #4CAF50;
            display: none;
        }
        .loading.show {
            display: block;
        }
        .error {
            background: #f44336;
            color: white;
            padding: 15px;
            border-radius: 4px;
            margin-top: 20px;
            display: none;
        }
        .error.show {
            display: block;
        }
        .row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        @media (max-width: 768px) {
            .row {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Freqtrade Data Check</h1>
        <div style="background: #2a5a2a; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #4CAF50;">
            <strong>⚠️ Important:</strong> You must be logged into FreqUI first! 
            Open <a href="/" style="color: #4CAF50;">FreqUI</a> in another tab, login, then come back to this page.
        </div>
        
        <div class="form-group">
            <label for="pair">Trading Pair</label>
            <input type="text" id="pair" placeholder="BTC/USDT" value="BTC/USDT">
        </div>
        
        <div class="row">
            <div class="form-group">
                <label for="timeframe">Timeframe</label>
                <select id="timeframe">
                    <option value="1m">1m</option>
                    <option value="5m" selected>5m</option>
                    <option value="15m">15m</option>
                    <option value="1h">1h</option>
                    <option value="4h">4h</option>
                    <option value="1d">1d</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="timerange">Timerange (optional, e.g., 20260201-20260301)</label>
                <input type="text" id="timerange" placeholder="20260201-20260301">
            </div>
        </div>
        
        <button id="checkBtn" onclick="checkData()">Check Data</button>
        
        <div class="loading" id="loading">Checking data...</div>
        <div class="error" id="error"></div>
        
        <div class="results" id="results">
            <div class="status-card" id="statusCard">
                <h2 id="statusTitle">Data Status</h2>
                <div class="stat">
                    <span class="stat-label">Status:</span>
                    <span class="stat-value" id="status">-</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Completeness:</span>
                    <span class="stat-value" id="completeness">-</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Total Candles:</span>
                    <span class="stat-value" id="totalCandles">-</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Expected Candles:</span>
                    <span class="stat-value" id="expectedCandles">-</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Missing Candles:</span>
                    <span class="stat-value" id="missingCandles">-</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Zero Volume Candles:</span>
                    <span class="stat-value" id="zeroVolume">-</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Data Start:</span>
                    <span class="stat-value" id="dataStart">-</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Data End:</span>
                    <span class="stat-value" id="dataEnd">-</span>
                </div>
            </div>
            
            <div class="gaps" id="gapsSection" style="display: none;">
                <h3 style="color: #ff9800; margin-bottom: 15px;">⚠️ Data Gaps Found</h3>
                <div id="gapsList"></div>
            </div>
        </div>
    </div>
    
    <script>
        // Get JWT token from localStorage (FreqUI stores it here)
        function getAuthToken() {
            // Try common localStorage keys used by FreqUI
            const tokenKeys = ['access_token', 'token', 'jwt_token', 'auth_token'];
            for (const key of tokenKeys) {
                const token = localStorage.getItem(key);
                if (token) {
                    return token;
                }
            }
            // Also check for keys with prefixes
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                if (key && (key.includes('token') || key.includes('auth'))) {
                    const token = localStorage.getItem(key);
                    if (token && token.startsWith('eyJ')) { // JWT tokens start with 'eyJ'
                        return token;
                    }
                }
            }
            return null;
        }
        
        async function checkData() {
            const pair = document.getElementById('pair').value.trim();
            const timeframe = document.getElementById('timeframe').value;
            const timerange = document.getElementById('timerange').value.trim();
            
            if (!pair) {
                showError('Please enter a trading pair');
                return;
            }
            
            // Show loading
            document.getElementById('loading').classList.add('show');
            document.getElementById('error').classList.remove('show');
            document.getElementById('results').classList.remove('show');
            document.getElementById('checkBtn').disabled = true;
            
            try {
                // Build URL
                let url = `/api/v1/check_data?pair=${encodeURIComponent(pair)}&timeframe=${encodeURIComponent(timeframe)}`;
                if (timerange) {
                    url += `&timerange=${encodeURIComponent(timerange)}`;
                }
                
                // Prepare headers
                const headers = {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                };
                
                // Try to get JWT token from localStorage
                const token = getAuthToken();
                if (token) {
                    headers['Authorization'] = `Bearer ${token}`;
                }
                
                // Make request with credentials
                const response = await fetch(url, {
                    method: 'GET',
                    credentials: 'include',
                    headers: headers
                });
                
                if (!response.ok) {
                    if (response.status === 401) {
                        // Try to get token from sessionStorage or prompt for credentials
                        const sessionToken = sessionStorage.getItem('access_token') || 
                                           sessionStorage.getItem('token');
                        if (sessionToken && !token) {
                            // Retry with session token
                            headers['Authorization'] = `Bearer ${sessionToken}`;
                            const retryResponse = await fetch(url, {
                                method: 'GET',
                                credentials: 'include',
                                headers: headers
                            });
                            if (retryResponse.ok) {
                                const data = await retryResponse.json();
                                displayResults(data);
                                return;
                            }
                        }
                        throw new Error('Authentication required. Please login to FreqUI first, then refresh this page.');
                    }
                    const errorText = await response.text();
                    let errorMsg = `Error: ${response.status}`;
                    try {
                        const errorJson = JSON.parse(errorText);
                        errorMsg = errorJson.detail || errorMsg;
                    } catch (e) {
                        errorMsg = errorText || errorMsg;
                    }
                    throw new Error(errorMsg);
                }
                
                const data = await response.json();
                displayResults(data);
                
            } catch (error) {
                showError(error.message || 'Failed to check data. Make sure you are logged in to FreqUI first.');
            } finally {
                document.getElementById('loading').classList.remove('show');
                document.getElementById('checkBtn').disabled = false;
            }
        }
        
        function displayResults(data) {
            // Update status card
            const statusCard = document.getElementById('statusCard');
            statusCard.className = 'status-card status-' + data.status;
            
            document.getElementById('status').textContent = data.status.toUpperCase();
            document.getElementById('completeness').textContent = data.completeness_percent + '%';
            document.getElementById('totalCandles').textContent = data.total_candles.toLocaleString();
            document.getElementById('expectedCandles').textContent = data.expected_candles ? data.expected_candles.toLocaleString() : 'N/A';
            document.getElementById('missingCandles').textContent = data.missing_candles.toLocaleString();
            document.getElementById('zeroVolume').textContent = data.zero_volume_candles.toLocaleString();
            document.getElementById('dataStart').textContent = data.data_start || 'N/A';
            document.getElementById('dataEnd').textContent = data.data_end || 'N/A';
            
            // Display gaps
            const gapsSection = document.getElementById('gapsSection');
            const gapsList = document.getElementById('gapsList');
            
            if (data.gaps && data.gaps.length > 0) {
                gapsSection.style.display = 'block';
                gapsList.innerHTML = '';
                data.gaps.forEach((gap, index) => {
                    const gapDiv = document.createElement('div');
                    gapDiv.className = 'gap-item';
                    gapDiv.innerHTML = `
                        <strong>Gap ${index + 1}</strong><br>
                        From: ${gap.start}<br>
                        To: ${gap.end}<br>
                        Missing Candles: ${gap.missing_candles}
                    `;
                    gapsList.appendChild(gapDiv);
                });
            } else {
                gapsSection.style.display = 'none';
            }
            
            // Show results
            document.getElementById('results').classList.add('show');
        }
        
        function showError(message) {
            const errorDiv = document.getElementById('error');
            errorDiv.textContent = message;
            errorDiv.classList.add('show');
        }
        
        // Allow Enter key to submit
        document.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                checkData();
            }
        });
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


@router_ui.get("/{rest_of_path:path}")
async def index_html(rest_of_path: str):
    """
    Emulate path fallback to index.html.
    """
    if rest_of_path.startswith("api") or rest_of_path.startswith("."):
        raise HTTPException(status_code=404, detail="Not Found")
    uibase = (Path(__file__).parent / "ui/installed/").resolve()
    filename = (uibase / rest_of_path).resolve()
    # It's security relevant to check "relative_to".
    # Without this, Directory-traversal is possible.
    media_type: str | None = None
    if filename.suffix == ".js":
        # Force text/javascript for .js files - Circumvent faulty system configuration
        media_type = "application/javascript"
    if filename.is_file() and filename.is_relative_to(uibase):
        return FileResponse(str(filename), media_type=media_type)

    index_file = uibase / "index.html"
    if not index_file.is_file():
        return FileResponse(str(uibase.parent / "fallback_file.html"))
    
    # Inject navigation script into index.html for FreqUI
    if rest_of_path == "" or rest_of_path == "/":
        try:
            with open(index_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Check if injection script already exists
            if "freqtrade-check-data-nav" not in content:
                # Inject script before closing </body> tag
                injection_script = """
    <!-- Freqtrade Check Data Navigation Injection -->
    <script>
    (function() {
        console.log('[Freqtrade] Check Data navigation injection script loaded');
        
        function findNavigationContainer() {
            // Strategy 1: Look for elements containing navigation text
            const searchTexts = ['Chart', 'Backtest', 'Download Data', 'Pairlist', 'Config'];
            const allElements = document.querySelectorAll('*');
            
            for (const el of allElements) {
                const text = (el.textContent || '').trim();
                const hasMultipleNavItems = searchTexts.filter(t => text.includes(t)).length >= 2;
                
                if (hasMultipleNavItems) {
                    // Check if it's a navigation-like element
                    const tagName = el.tagName.toLowerCase();
                    const role = el.getAttribute('role');
                    const className = el.className || '';
                    
                    if (tagName === 'nav' || 
                        tagName === 'div' || 
                        tagName === 'ul' ||
                        role === 'navigation' ||
                        className.includes('nav') ||
                        className.includes('menu') ||
                        className.includes('toolbar')) {
                        console.log('[Freqtrade] Found navigation container:', el);
                        return el;
                    }
                }
            }
            
            // Strategy 2: Look for links with specific hrefs
            const navLinks = ['/backtest', '/download', '/pairlist'];
            for (const linkText of navLinks) {
                const links = Array.from(document.querySelectorAll('a, [role="link"], router-link'));
                const matchingLink = links.find(link => {
                    const href = (link.getAttribute('href') || link.getAttribute('to') || '').toLowerCase();
                    return href.includes(linkText);
                });
                
                if (matchingLink) {
                    // Walk up the DOM tree to find container
                    let parent = matchingLink.parentElement;
                    let depth = 0;
                    while (parent && depth < 5) {
                        const siblings = Array.from(parent.children || []);
                        const navLinkCount = siblings.filter(s => {
                            const sText = (s.textContent || '').toLowerCase();
                            return searchTexts.some(t => sText.includes(t.toLowerCase()));
                        }).length;
                        
                        if (navLinkCount >= 2) {
                            console.log('[Freqtrade] Found navigation container via link parent:', parent);
                            return parent;
                        }
                        parent = parent.parentElement;
                        depth++;
                    }
                }
            }
            
            // Strategy 3: Look for header/toolbar elements
            const headerSelectors = ['header', '.v-toolbar', '.toolbar', '[role="banner"]'];
            for (const selector of headerSelectors) {
                const elements = document.querySelectorAll(selector);
                for (const el of elements) {
                    const text = (el.textContent || '').trim();
                    if (searchTexts.filter(t => text.includes(t)).length >= 2) {
                        console.log('[Freqtrade] Found navigation container via header:', el);
                        return el;
                    }
                }
            }
            
            console.warn('[Freqtrade] Could not find navigation container');
            return null;
        }
        
        function createCheckDataLink() {
            const link = document.createElement('a');
            link.id = 'freqtrade-check-data-link';
            link.href = '/check-data';
            link.textContent = 'Check Data';
            link.setAttribute('data-freqtrade-injected', 'true');
            
            // Base styles
            link.style.cssText = `
                color: inherit;
                text-decoration: none;
                padding: 8px 16px;
                display: inline-block;
                cursor: pointer;
                transition: opacity 0.2s;
            `;
            
            link.onmouseover = function() { this.style.opacity = '0.7'; };
            link.onmouseout = function() { this.style.opacity = '1'; };
            
            return link;
        }
        
        function injectCheckDataNav() {
            // Skip if already injected
            if (document.getElementById('freqtrade-check-data-link')) {
                return true;
            }
            
            const navContainer = findNavigationContainer();
            if (!navContainer) {
                return false;
            }
            
            // Find existing navigation links
            const allLinks = Array.from(navContainer.querySelectorAll('a, [role="link"], router-link'));
            const navLinkTexts = ['Download Data', 'Backtest', 'Download', 'Pairlist', 'Config'];
            
            // Find a reference link to insert after
            let referenceLink = null;
            for (const linkText of navLinkTexts) {
                referenceLink = allLinks.find(link => {
                    const text = (link.textContent || '').trim();
                    return text.includes(linkText);
                });
                if (referenceLink) break;
            }
            
            const checkDataLink = createCheckDataLink();
            
            // Try to match styles from existing links
            if (allLinks.length > 0) {
                const refLink = referenceLink || allLinks[0];
                const computedStyle = window.getComputedStyle(refLink);
                checkDataLink.style.color = computedStyle.color;
                checkDataLink.style.fontSize = computedStyle.fontSize;
                checkDataLink.style.fontFamily = computedStyle.fontFamily;
                checkDataLink.style.fontWeight = computedStyle.fontWeight;
                checkDataLink.style.padding = computedStyle.padding || '8px 16px';
                checkDataLink.style.margin = computedStyle.margin || '0 4px';
            }
            
            // Insert the link
            if (referenceLink && referenceLink.parentElement) {
                // Insert after the reference link's parent (for list items)
                const parent = referenceLink.parentElement;
                if (parent.tagName === 'LI') {
                    const newLi = document.createElement('li');
                    newLi.appendChild(checkDataLink);
                    parent.insertAdjacentElement('afterend', newLi);
                } else {
                    referenceLink.insertAdjacentElement('afterend', checkDataLink);
                }
                console.log('[Freqtrade] Check Data link inserted after:', referenceLink.textContent);
            } else {
                // Append to container
                if (navContainer.tagName === 'UL') {
                    const li = document.createElement('li');
                    li.appendChild(checkDataLink);
                    navContainer.appendChild(li);
                } else {
                    navContainer.appendChild(checkDataLink);
                }
                console.log('[Freqtrade] Check Data link appended to container');
            }
            
            return true;
        }
        
        // Use MutationObserver to watch for DOM changes (Vue dynamic rendering)
        const observer = new MutationObserver(function(mutations) {
            if (!document.getElementById('freqtrade-check-data-link')) {
                injectCheckDataNav();
            }
        });
        
        // Start observing when DOM is ready
        function startObserving() {
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
            console.log('[Freqtrade] MutationObserver started');
        }
        
        // Try injection immediately
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                injectCheckDataNav();
                startObserving();
            });
        } else {
            injectCheckDataNav();
            startObserving();
        }
        
        // Also try at intervals (fallback)
        let attempts = 0;
        const maxAttempts = 20;
        const interval = setInterval(function() {
            attempts++;
            if (injectCheckDataNav() || attempts >= maxAttempts) {
                clearInterval(interval);
                if (attempts >= maxAttempts && !document.getElementById('freqtrade-check-data-link')) {
                    console.warn('[Freqtrade] Failed to inject Check Data link after', maxAttempts, 'attempts');
                }
            }
        }, 500);
        
        // Try again after longer delays (Vue might load slowly)
        setTimeout(injectCheckDataNav, 1000);
        setTimeout(injectCheckDataNav, 3000);
        setTimeout(injectCheckDataNav, 5000);
    })();
    </script>
"""
                # Insert before closing </body> tag
                if "</body>" in content:
                    content = content.replace("</body>", injection_script + "\n</body>")
                elif "</html>" in content:
                    content = content.replace("</html>", injection_script + "\n</html>")
                else:
                    content += injection_script
            
            return HTMLResponse(content=content)
        except Exception as e:
            # If injection fails, fall back to regular file serving
            logger.warning(f"Failed to inject navigation script: {e}")
            return FileResponse(str(index_file))
    
    # Fall back to index.html, as indicated by vue router docs
    return FileResponse(str(index_file))
