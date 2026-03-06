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
        "ema_20": {"color": "blue"},  # Must match column name from populate_indicators
    },
    "subplots": {
        "RSI": {
            "rsi": {"color": "red"},  # Must match column name
        }
    }
}
```

## Common Indicators Examples

### Moving Averages

```python
# In populate_indicators:
dataframe["sma_20"] = ta.SMA(dataframe, timeperiod=20)
dataframe["ema_20"] = ta.EMA(dataframe, timeperiod=20)
dataframe["ema_50"] = ta.EMA(dataframe, timeperiod=50)

# In plot_config:
"main_plot": {
    "sma_20": {"color": "blue"},
    "ema_20": {"color": "green"},
    "ema_50": {"color": "orange"},
}
```

### MACD

```python
# In populate_indicators:
macd = ta.MACD(dataframe)
dataframe["macd"] = macd["macd"]
dataframe["macdsignal"] = macd["macdsignal"]
dataframe["macdhist"] = macd["macdhist"]

# In plot_config:
"subplots": {
    "MACD": {
        "macd": {"color": "blue"},
        "macdsignal": {"color": "orange"},
        "macdhist": {"type": "bar", "plotly": {"opacity": 0.9}},
    }
}
```

### Bollinger Bands

```python
# In populate_indicators:
bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
dataframe["bb_lowerband"] = bollinger["lower"]
dataframe["bb_upperband"] = bollinger["upper"]
dataframe["bb_middleband"] = bollinger["mid"]

# In plot_config:
# Bollinger bands are AUTO-DETECTED if bb_lowerband and bb_upperband exist
# No need to add to plot_config - they appear as shaded area automatically
```

### RSI with Threshold Lines

```python
# In populate_indicators:
dataframe["rsi"] = ta.RSI(dataframe)
# Add threshold lines (optional)
dataframe["rsi_buy"] = 30  # Your buy threshold
dataframe["rsi_sell"] = 70  # Your sell threshold

# In plot_config:
"subplots": {
    "RSI": {
        "rsi": {"color": "red"},
        "rsi_buy": {"color": "green", "type": "line"},
        "rsi_sell": {"color": "red", "type": "line"},
    }
}
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

## Example: Complete Strategy with Multiple Indicators

```python
def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    # RSI
    dataframe["rsi"] = ta.RSI(dataframe)
    
    # Moving Averages
    dataframe["ema_20"] = ta.EMA(dataframe, timeperiod=20)
    dataframe["ema_50"] = ta.EMA(dataframe, timeperiod=50)
    
    # MACD
    macd = ta.MACD(dataframe)
    dataframe["macd"] = macd["macd"]
    dataframe["macdsignal"] = macd["macdsignal"]
    dataframe["macdhist"] = macd["macdhist"]
    
    return dataframe

plot_config = {
    "main_plot": {
        "ema_20": {"color": "blue"},
        "ema_50": {"color": "orange"},
    },
    "subplots": {
        "RSI": {
            "rsi": {"color": "red"},
        },
        "MACD": {
            "macd": {"color": "blue"},
            "macdsignal": {"color": "orange"},
            "macdhist": {"type": "bar"},
        }
    }
}
```

## Viewing Charts

After adding indicators to `plot_config`:

1. **In Web UI:** Charts automatically show configured indicators
2. **Backtesting:** Use `freqtrade plot-dataframe` command
3. **Live Trading:** Charts update in real-time in Web UI

## Troubleshooting

**Indicator not showing?**
- Check column name matches exactly
- Make sure indicator is calculated in `populate_indicators()`
- Check logs for warnings about missing indicators

**Too many indicators?**
- Remove unused indicators from `populate_indicators()` for better performance
- Only plot indicators you actually use in your strategy logic
