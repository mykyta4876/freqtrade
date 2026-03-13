from pathlib import Path

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse
from starlette.responses import FileResponse


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
                
                // Get credentials from browser (if available) or prompt
                const response = await fetch(url, {
                    credentials: 'include',
                    headers: {
                        'Accept': 'application/json'
                    }
                });
                
                if (!response.ok) {
                    if (response.status === 401) {
                        throw new Error('Authentication required. Please login to FreqUI first.');
                    }
                    const errorText = await response.text();
                    throw new Error(`Error: ${response.status} - ${errorText}`);
                }
                
                const data = await response.json();
                displayResults(data);
                
            } catch (error) {
                showError(error.message || 'Failed to check data. Make sure you are logged in to FreqUI.');
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
    # Fall back to index.html, as indicated by vue router docs
    return FileResponse(str(index_file))
