# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file
# --- Do not remove these imports ---
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
from pandas import DataFrame
from typing import Dict, Optional, Union, Tuple

from freqtrade.strategy import (
    IStrategy,
    Trade,
    Order,
    PairLocks,
    informative,
    # Hyperopt Parameters
    BooleanParameter,
    CategoricalParameter,
    DecimalParameter,
    IntParameter,
    RealParameter,
    # timeframe helpers
    timeframe_to_minutes,
    timeframe_to_next_date,
    timeframe_to_prev_date,
    # Strategy helper functions
    merge_informative_pair,
    stoploss_from_absolute,
    stoploss_from_open,
    AnnotationType,
)

# --------------------------------
# Add your lib to import here
import talib.abstract as ta
from technical import qtpylib


class MyFirstStrategy(IStrategy):
    """
    My First Trading Strategy
    
    A simple RSI-based strategy to get you started with freqtrade.
    This strategy uses RSI (Relative Strength Index) to identify entry and exit points.
    
    Entry: When RSI crosses above the buy threshold (default: 30)
    Exit: When RSI crosses above the sell threshold (default: 70)
    
    More information: https://www.freqtrade.io/en/stable/strategy-customization/
    """
    # Strategy interface version
    INTERFACE_VERSION = 3

    # Optimal timeframe for the strategy
    timeframe = "5m"

    # Can this strategy go short?
    can_short: bool = False

    # Minimal ROI designed for the strategy
    minimal_roi = {
        "60": 0.01,  # Exit after 60 minutes if profit is 1%
        "30": 0.02,  # Exit after 30 minutes if profit is 2%
        "0": 0.04    # Exit immediately if profit is 4%
    }

    # Optimal stoploss designed for the strategy
    stoploss = -0.10  # Stop loss at -10%

    # Trailing stoploss
    trailing_stop = False

    # Run "populate_indicators()" only for new candle
    process_only_new_candles = True

    # These values can be overridden in the config
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 30

    # Strategy parameters (can be optimized with hyperopt)
    buy_rsi = IntParameter(10, 40, default=30, space="buy", optimize=True, load=True)
    sell_rsi = IntParameter(60, 90, default=70, space="sell", optimize=True, load=True)

    # Plot configuration for chart visualization
    # Add indicators here that you want to see in the Web UI charts
    plot_config = {
        # Main plot indicators (shown on price chart)
        # These overlay on the candlestick chart
        "main_plot": {
            # Uncomment to add moving averages:
            # "ema_20": {"color": "blue", "type": "line"},
            # "ema_50": {"color": "orange", "type": "line"},
            # "sma_20": {"color": "green", "type": "line"},
            
            # Bollinger Bands (automatically shown as shaded area if bb_lowerband/bb_upperband exist)
            # No need to add here - they're auto-detected
        },
        # Subplots (shown below main chart in separate panels)
        "subplots": {
            "RSI": {
                "rsi": {"color": "red"},
                # Add horizontal lines for buy/sell thresholds
                # "buy_rsi_line": {"color": "green", "type": "line"},  # if you add this indicator
                # "sell_rsi_line": {"color": "red", "type": "line"},   # if you add this indicator
            },
            # Uncomment to add MACD subplot:
            # "MACD": {
            #     "macd": {"color": "blue"},
            #     "macdsignal": {"color": "orange"},
            #     "macdhist": {"type": "bar", "plotly": {"opacity": 0.9}},
            # },
        }
    }

    def informative_pairs(self):
        """
        Define additional, informative pair/interval combinations to be cached from the exchange.
        :return: List of tuples in the format (pair, interval)
        """
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Adds technical indicators to the given DataFrame
        
        :param dataframe: Dataframe with data from the exchange
        :param metadata: Additional information, like the currently traded pair
        :return: a Dataframe with all mandatory indicators for the strategies
        """
        # RSI - Relative Strength Index
        dataframe["rsi"] = ta.RSI(dataframe)
        
        # Optional: Add more indicators for visualization
        # Uncomment the ones you want to see in charts:
        
        # Moving Averages (shown on main price chart)
        # dataframe["ema_20"] = ta.EMA(dataframe, timeperiod=20)
        # dataframe["ema_50"] = ta.EMA(dataframe, timeperiod=50)
        # dataframe["sma_20"] = ta.SMA(dataframe, timeperiod=20)
        
        # MACD (shown in subplot)
        # macd = ta.MACD(dataframe)
        # dataframe["macd"] = macd["macd"]
        # dataframe["macdsignal"] = macd["macdsignal"]
        # dataframe["macdhist"] = macd["macdhist"]
        
        # Bollinger Bands (shown on main chart as shaded area)
        # bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
        # dataframe["bb_lowerband"] = bollinger["lower"]
        # dataframe["bb_middleband"] = bollinger["mid"]
        # dataframe["bb_upperband"] = bollinger["upper"]

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the entry signal for the given dataframe
        :param dataframe: DataFrame
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with entry columns populated
        """
        dataframe.loc[
            (
                (qtpylib.crossed_above(dataframe["rsi"], self.buy_rsi.value)) &  # RSI crosses above buy threshold
                (dataframe["volume"] > 0)  # Make sure Volume is not 0
            ),
            "enter_long"] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the exit signal for the given dataframe
        :param dataframe: DataFrame
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with exit columns populated
        """
        dataframe.loc[
            (
                (qtpylib.crossed_above(dataframe["rsi"], self.sell_rsi.value)) &  # RSI crosses above sell threshold
                (dataframe["volume"] > 0)  # Make sure Volume is not 0
            ),
            "exit_long"] = 1

        return dataframe
