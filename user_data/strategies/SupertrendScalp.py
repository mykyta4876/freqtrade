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


class SupertrendScalp(IStrategy):
    """
    Supertrend-based 1m scalping strategy (higher-quality entries).

    Core idea:
    - Compute Supertrend (ATR-based) trend direction.
    - Enter long on Supertrend flip to bullish.
    - Avoid entering too early in downtrends using EMA200 / EMA trend filter.

    Notes:
    - Designed for 1m candles. Ensure config timeframe matches.
    - Parameters are tunable in FreqUI backtest UI.
    """

    INTERFACE_VERSION = 3
    timeframe = "1m"
    can_short: bool = False

    # Conservative defaults for 1m scalping
    minimal_roi = {
        "15": 0.002,
        "5": 0.001,
        "0": 0.0,
    }

    stoploss = -0.02
    trailing_stop = False

    process_only_new_candles = True
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    # Need enough candles for EMA200 + ATR
    startup_candle_count: int = 250

    # --- Tunable parameters (visible in FreqUI / Backtest) ---
    st_atr_period = IntParameter(7, 30, default=10, space="buy", optimize=True, load=True)
    st_multiplier = DecimalParameter(1.0, 5.0, default=3.0, decimals=1, space="buy", optimize=True, load=True)

    ema_fast = IntParameter(10, 50, default=20, space="buy", optimize=True, load=True)
    ema_slow = IntParameter(30, 120, default=50, space="buy", optimize=True, load=True)

    # Optional momentum confirmation to reduce false flips in chop
    use_rsi_filter = BooleanParameter(default=True, space="buy", optimize=True, load=True)
    rsi_period = IntParameter(7, 21, default=14, space="buy", optimize=True, load=True)
    rsi_min = IntParameter(45, 60, default=50, space="buy", optimize=True, load=True)

    plot_config = {
        "main_plot": {
            "supertrend": {"color": "lime"},
            "ema_fast": {"color": "deepskyblue"},
            "ema_slow": {"color": "orange"},
            "ema_200": {"color": "gray"},
        },
        "subplots": {
            "RSI": {
                "rsi": {"color": "red"},
                "rsi_min": {"color": "yellow"},
            },
        },
    }

    @staticmethod
    def _supertrend(
        dataframe: DataFrame,
        atr_period: int,
        multiplier: float,
    ) -> tuple[pd.Series, pd.Series, pd.Series]:
        """
        Compute Supertrend.

        Returns:
        - supertrend: The supertrend line (final band depending on trend direction)
        - direction: 1 for bullish, -1 for bearish
        - hl2: (high+low)/2
        """
        df = dataframe.copy()
        hl2 = (df["high"] + df["low"]) / 2.0
        atr = ta.ATR(df, timeperiod=atr_period)

        basic_ub = hl2 + (multiplier * atr)
        basic_lb = hl2 - (multiplier * atr)

        final_ub = basic_ub.copy()
        final_lb = basic_lb.copy()

        # Initialize
        direction = pd.Series(index=df.index, data=1, dtype="int8")
        supertrend = pd.Series(index=df.index, data=np.nan, dtype="float64")

        # Find first index where ATR is valid - before that supertrend cannot be computed.
        first_valid = int(atr.first_valid_index()) if atr.first_valid_index() is not None else len(df)

        # Seed initial values at first_valid to avoid NaN propagation.
        if 0 <= first_valid < len(df):
            final_ub.iat[first_valid] = basic_ub.iat[first_valid]
            final_lb.iat[first_valid] = basic_lb.iat[first_valid]
            direction.iat[first_valid] = 1
            supertrend.iat[first_valid] = final_lb.iat[first_valid]

        for i in range(first_valid + 1, len(df)):
            # Final upper band
            prev_final_ub = final_ub.iat[i - 1]
            if np.isnan(prev_final_ub):
                final_ub.iat[i] = basic_ub.iat[i]
            elif (basic_ub.iat[i] < prev_final_ub) or (df["close"].iat[i - 1] > prev_final_ub):
                final_ub.iat[i] = basic_ub.iat[i]
            else:
                final_ub.iat[i] = final_ub.iat[i - 1]

            # Final lower band
            prev_final_lb = final_lb.iat[i - 1]
            if np.isnan(prev_final_lb):
                final_lb.iat[i] = basic_lb.iat[i]
            elif (basic_lb.iat[i] > prev_final_lb) or (df["close"].iat[i - 1] < prev_final_lb):
                final_lb.iat[i] = basic_lb.iat[i]
            else:
                final_lb.iat[i] = final_lb.iat[i - 1]

            # Direction
            # Use previous bands for direction decision (common supertrend definition)
            if df["close"].iat[i] > final_ub.iat[i - 1]:
                direction.iat[i] = 1
            elif df["close"].iat[i] < final_lb.iat[i - 1]:
                direction.iat[i] = -1
            else:
                direction.iat[i] = direction.iat[i - 1]

            # Supertrend line
            supertrend.iat[i] = final_lb.iat[i] if direction.iat[i] == 1 else final_ub.iat[i]

        return supertrend, direction, hl2

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # EMAs (trend filter + structure)
        dataframe["ema_fast"] = ta.EMA(dataframe, timeperiod=int(self.ema_fast.value))
        dataframe["ema_slow"] = ta.EMA(dataframe, timeperiod=int(self.ema_slow.value))
        dataframe["ema_200"] = ta.EMA(dataframe, timeperiod=200)

        # RSI (optional confirmation)
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=int(self.rsi_period.value))
        dataframe["rsi_min"] = float(self.rsi_min.value)

        # Supertrend
        st, direction, _ = self._supertrend(
            dataframe,
            atr_period=int(self.st_atr_period.value),
            multiplier=float(self.st_multiplier.value),
        )
        dataframe["supertrend"] = st
        dataframe["st_dir"] = direction  # 1 bullish, -1 bearish

        # Trend filter to avoid early entries in downtrend
        dataframe["trend_ok"] = (
            (dataframe["close"] > dataframe["ema_200"]) &
            (dataframe["ema_fast"] > dataframe["ema_slow"])
        )

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Enter on supertrend turning bullish (flip from -1 to 1)
        st_flip_bull = (dataframe["st_dir"] == 1) & (dataframe["st_dir"].shift(1) == -1)

        rsi_ok = (dataframe["rsi"] >= self.rsi_min.value)
        if not self.use_rsi_filter.value:
            rsi_ok = pd.Series(index=dataframe.index, data=True)

        dataframe.loc[
            (
                (dataframe["volume"] > 0) &
                st_flip_bull &
                (dataframe["trend_ok"]) &
                rsi_ok
            ),
            "enter_long",
        ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Exit on supertrend turning bearish (flip from 1 to -1)
        st_flip_bear = (dataframe["st_dir"] == -1) & (dataframe["st_dir"].shift(1) == 1)

        dataframe.loc[
            (
                (dataframe["volume"] > 0) &
                st_flip_bear
            ),
            "exit_long",
        ] = 1

        return dataframe

