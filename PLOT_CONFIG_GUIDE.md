# Plot Configuration Guide - Adding Indicators to Charts

## Overview

The `plot_config` in your strategy controls which indicators appear in the Web UI charts and backtesting visualizations.

## Structure

```python
plot_config = {
    "main_plot": {
        # Indicators shown ON the price chart (overlay)
    },
    "subplots": {
        # Indicators shown BELOW the price chart (separate panels)
    }
}
```

## Main Plot Indicators

These overlay on the candlestick chart. Good for:
- Moving averages (SMA, EMA)
- Bollinger Bands (auto-detected, no need to add)
- Support/Resistance levels
- Price-based indicators

### Example:

```python
"main_plot": {
    "ema_20": {"color": "blue"},
    "ema_50": {"color": "orange"},
    "sma_200": {"color": "gray"},
}
```

**Important:** You must calculate these indicators in `populate_indicators()` first!

## Subplot Indicators

These appear in separate panels below the main chart. Good for:
- RSI, MACD, Stochastic
- Volume indicators
- Oscillators
- Any indicator with different scale than price

### Example:

```python
"subplots": {
    "RSI": {
        "rsi": {"color": "red"},
    },
    "MACD": {
        "macd": {"color": "blue"},
        "macdsignal": {"color": "orange"},
        "macdhist": {"type": "bar"},
    },
    "Volume": {
        "volume": {"type": "bar", "color": "gray"},
    }
}
```

## Adding Indicators Step-by-Step

### Step 1: Calculate Indicator in `populate_indicators()`

```python
def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    # Calculate the indicator
    dataframe["ema_20"] = ta.EMA(dataframe, timeperiod=20)
    dataframe["rsi"] = ta.RSI(dataframe)
    
    return dataframe
```

### Step 2: Add to `plot_config`

```python
plot_config = {
    "main_plot": {
        "ema_20": {"color": "blue"},
    },
    "subplots": {
        "RSI": {
            "rsi": {"color": "red"},
        }
    }
}
```

## Your Updated Strategy

I've updated your `MyFirstStrategy.py` to include:

✅ **Main Plot:**
- EMA 20 (blue line)
- EMA 50 (orange line)

✅ **Subplots:**
- RSI (red line) with buy/sell threshold lines
- MACD (blue line, orange signal, histogram bars)

## Viewing in Web UI

After updating your strategy:

1. **Restart the webserver** (if running)
2. **Run a new backtest** to see the indicators
3. **View in Web UI:** The charts will automatically show all configured indicators

## Common Indicators You Can Add

### Moving Averages
```python
dataframe["sma_20"] = ta.SMA(dataframe, timeperiod=20)
dataframe["ema_20"] = ta.EMA(dataframe, timeperiod=20)
dataframe["ema_50"] = ta.EMA(dataframe, timeperiod=50)
```

### MACD
```python
macd = ta.MACD(dataframe)
dataframe["macd"] = macd["macd"]
dataframe["macdsignal"] = macd["macdsignal"]
dataframe["macdhist"] = macd["macdhist"]
```

### Bollinger Bands
```python
bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
dataframe["bb_lowerband"] = bollinger["lower"]
dataframe["bb_middleband"] = bollinger["mid"]
dataframe["bb_upperband"] = bollinger["upper"]
# Auto-detected in plot - no need to add to plot_config
```

### Stochastic
```python
stoch = ta.STOCH(dataframe)
dataframe["slowd"] = stoch["slowd"]
dataframe["slowk"] = stoch["slowk"]
```

## Plot Configuration Options

### Color Options

```python
"indicator_name": {"color": "red"}        # Named color
"indicator_name": {"color": "#FF0000"}   # Hex color
"indicator_name": {"color": "rgb(255,0,0)"}  # RGB color
```

### Plot Types

```python
"indicator_name": {"type": "scatter"}   # Line plot (default)
"indicator_name": {"type": "bar"}        # Bar chart
```

### Advanced Plotly Options

```python
"indicator_name": {
    "color": "blue",
    "plotly": {
        "line": {"width": 2, "dash": "dash"},  # Dashed line
        "opacity": 0.7,  # Transparency
    }
}
```

## Tips

1. **Column names must match:** The key in `plot_config` must exactly match the column name in `dataframe`
2. **Calculate first:** Always calculate indicators in `populate_indicators()` before adding to `plot_config`
3. **Performance:** Only calculate indicators you actually use - don't calculate everything just for plotting
4. **Bollinger Bands:** Automatically detected - no need to add to `plot_config`
5. **Volume:** Usually shown automatically, but you can customize it

## Troubleshooting

**Indicator not showing?**
- Check column name matches exactly
- Make sure indicator is calculated in `populate_indicators()`
- Check logs for warnings about missing indicators

**Too many indicators?**
- Remove unused indicators from `populate_indicators()` for better performance
- Only plot indicators you actually use in your strategy logic
