# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file
import math
import numpy as np
import pandas as pd
from datetime import datetime
from pandas import DataFrame
from typing import Optional

from freqtrade.strategy import (
    IStrategy,
    BooleanParameter,
    CategoricalParameter,
    DecimalParameter,
    IntParameter,
    stoploss_from_absolute,
)
from freqtrade.persistence import Trade
import talib.abstract as ta
from technical import qtpylib


class EMASupertrendAdvanced(IStrategy):
    """
    EMA crossover + Supertrend + multi-filter strategy.

    Dual-direction implementation (long + short).
    """

    INTERFACE_VERSION = 3
    can_short: bool = True
    timeframe = "1m"
    startup_candle_count: int = 300

    # Base protections
    minimal_roi = {
        "20": 0.004,
        "10": 0.002,
        "0": 0.0,
    }
    stoploss = -0.10
    use_custom_stoploss = True

    process_only_new_candles = True
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    # -----------------------------
    # EMA settings
    # -----------------------------
    ema_fast = IntParameter(5, 20, default=9, space="buy", optimize=True, load=True)
    ema_slow = IntParameter(30, 120, default=60, space="buy", optimize=True, load=True)
    ema_trend = IntParameter(100, 250, default=200, space="buy", optimize=True, load=True)
    use_trend_guard = BooleanParameter(default=False, space="buy", optimize=True, load=True)
    cross_lookback = IntParameter(1, 10, default=5, space="buy", optimize=True, load=True)
    use_recent_cross_confirm = BooleanParameter(default=False, space="buy", optimize=True, load=True)
    require_nonzero_volume = BooleanParameter(default=False, space="buy", optimize=True, load=True)

    # -----------------------------
    # Supertrend filter
    # -----------------------------
    use_supertrend = BooleanParameter(default=False, space="buy", optimize=True, load=True)
    st_atr_period = IntParameter(7, 20, default=10, space="buy", optimize=True, load=True)
    st_multiplier = DecimalParameter(1.5, 5.0, default=3.0, decimals=1, space="buy", optimize=True, load=True)

    # -----------------------------
    # ADX filter
    # -----------------------------
    use_adx_filter = BooleanParameter(default=False, space="buy", optimize=True, load=True)
    adx_period = IntParameter(7, 30, default=14, space="buy", optimize=True, load=True)
    adx_threshold = IntParameter(15, 30, default=20, space="buy", optimize=True, load=True)

    # -----------------------------
    # RSI filter
    # -----------------------------
    use_rsi_filter = BooleanParameter(default=False, space="buy", optimize=True, load=True)
    rsi_period = IntParameter(7, 21, default=14, space="buy", optimize=True, load=True)
    rsi_overbought = IntParameter(65, 80, default=75, space="buy", optimize=True, load=True)
    rsi_oversold = IntParameter(20, 35, default=25, space="buy", optimize=True, load=True)

    # -----------------------------
    # Volume filter
    # -----------------------------
    use_volume_filter = BooleanParameter(default=False, space="buy", optimize=True, load=True)
    volume_ma_period = IntParameter(10, 100, default=30, space="buy", optimize=True, load=True)
    volume_mult = DecimalParameter(0.8, 1.5, default=1.0, decimals=2, space="buy", optimize=True, load=True)

    # -----------------------------
    # Bollinger filter
    # -----------------------------
    use_bb_filter = BooleanParameter(default=False, space="buy", optimize=True, load=True)
    bb_mode = CategoricalParameter(
        ["avoid_extremes", "squeeze_only", "trend_position", "wide_bands"],
        default="avoid_extremes",
        space="buy",
        optimize=True,
        load=True,
    )
    bb_period = IntParameter(14, 50, default=20, space="buy", optimize=True, load=True)
    bb_std = DecimalParameter(1.5, 3.0, default=2.0, decimals=1, space="buy", optimize=True, load=True)
    bb_squeeze_width = DecimalParameter(0.01, 0.08, default=0.03, decimals=3, space="buy", optimize=True, load=True)
    bb_wide_width = DecimalParameter(0.03, 0.20, default=0.07, decimals=3, space="buy", optimize=True, load=True)

    # -----------------------------
    # Filter mode
    # -----------------------------
    filter_mode = CategoricalParameter(
        ["strict", "moderate", "relaxed", "score_based"],
        default="moderate",
        space="buy",
        optimize=True,
        load=True,
    )
    min_filter_score = IntParameter(1, 5, default=3, space="buy", optimize=True, load=True)

    # -----------------------------
    # ATR risk management
    # -----------------------------
    atr_period = IntParameter(7, 30, default=14, space="sell", optimize=True, load=True)
    use_atr_stoploss = BooleanParameter(default=True, space="sell", optimize=True, load=True)
    atr_sl_mult = DecimalParameter(1.0, 4.0, default=2.0, decimals=1, space="sell", optimize=True, load=True)

    use_atr_takeprofit = BooleanParameter(default=True, space="sell", optimize=True, load=True)
    atr_tp_mult = DecimalParameter(1.5, 6.0, default=3.0, decimals=1, space="sell", optimize=True, load=True)

    # Optional stake sizing by risk
    use_risk_position_size = BooleanParameter(default=False, space="buy", optimize=False, load=True)
    risk_per_trade = DecimalParameter(0.5, 3.0, default=2.0, decimals=1, space="buy", optimize=False, load=True)

    plot_config = {
        "main_plot": {
            "ema_5": {"color": "deepskyblue"},
            "ema_fast": {"color": "cyan"},
            "ema_10": {"color": "lightskyblue"},
            "ema_30": {"color": "orange"},
            "ema_slow": {"color": "gold"},
            "ema_trend": {"color": "gray"},
            "supertrend": {"color": "lime"},
            "bb_lowerband": {"color": "lightgray"},
            "bb_middleband": {"color": "silver"},
            "bb_upperband": {"color": "lightgray"},
        },
        "subplots": {
            "RSI": {
                "rsi": {"color": "red"},
            },
            "ADX": {
                "adx": {"color": "yellow"},
            },
            "BB Width": {
                "bb_width": {"color": "violet"},
            },
        },
    }

    @staticmethod
    def _supertrend(dataframe: DataFrame, atr_period: int, multiplier: float) -> tuple[pd.Series, pd.Series]:
        df = dataframe.copy()
        hl2 = (df["high"] + df["low"]) / 2.0
        atr = ta.ATR(df, timeperiod=atr_period)

        upperband = hl2 + multiplier * atr
        lowerband = hl2 - multiplier * atr

        final_upper = upperband.copy()
        final_lower = lowerband.copy()
        direction = pd.Series(index=df.index, data=1, dtype="int8")
        st = pd.Series(index=df.index, data=np.nan, dtype="float64")

        first_valid = atr.first_valid_index()
        if first_valid is None:
            return st, direction

        start = int(first_valid)
        final_upper.iat[start] = upperband.iat[start]
        final_lower.iat[start] = lowerband.iat[start]
        direction.iat[start] = 1
        st.iat[start] = final_lower.iat[start]

        for i in range(start + 1, len(df)):
            prev_fu = final_upper.iat[i - 1]
            prev_fl = final_lower.iat[i - 1]

            if np.isnan(prev_fu) or upperband.iat[i] < prev_fu or df["close"].iat[i - 1] > prev_fu:
                final_upper.iat[i] = upperband.iat[i]
            else:
                final_upper.iat[i] = prev_fu

            if np.isnan(prev_fl) or lowerband.iat[i] > prev_fl or df["close"].iat[i - 1] < prev_fl:
                final_lower.iat[i] = lowerband.iat[i]
            else:
                final_lower.iat[i] = prev_fl

            if df["close"].iat[i] > final_upper.iat[i - 1]:
                direction.iat[i] = 1
            elif df["close"].iat[i] < final_lower.iat[i - 1]:
                direction.iat[i] = -1
            else:
                direction.iat[i] = direction.iat[i - 1]

            st.iat[i] = final_lower.iat[i] if direction.iat[i] == 1 else final_upper.iat[i]

        return st, direction

    def _required_score(self, enabled_filters: int) -> int:
        if enabled_filters <= 0:
            return 0

        mode = self.filter_mode.value
        if mode == "strict":
            return enabled_filters
        if mode == "moderate":
            return math.ceil(enabled_filters * 0.75)
        if mode == "relaxed":
            return math.ceil(enabled_filters * 0.50)
        # score_based
        return min(int(self.min_filter_score.value), enabled_filters)

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Core EMA structure
        dataframe["ema_5"] = ta.EMA(dataframe, timeperiod=5)
        dataframe["ema_10"] = ta.EMA(dataframe, timeperiod=10)
        dataframe["ema_30"] = ta.EMA(dataframe, timeperiod=30)

        dataframe["ema_fast"] = ta.EMA(dataframe, timeperiod=int(self.ema_fast.value))
        dataframe["ema_slow"] = ta.EMA(dataframe, timeperiod=int(self.ema_slow.value))
        dataframe["ema_trend"] = ta.EMA(dataframe, timeperiod=int(self.ema_trend.value))

        # RSI / ADX / ATR
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=int(self.rsi_period.value))
        dataframe["adx"] = ta.ADX(dataframe, timeperiod=int(self.adx_period.value))
        dataframe["atr"] = ta.ATR(dataframe, timeperiod=int(self.atr_period.value))

        # Volume MA
        dataframe["volume_ma"] = ta.SMA(dataframe["volume"], timeperiod=int(self.volume_ma_period.value))

        # Bollinger
        bb = qtpylib.bollinger_bands(
            qtpylib.typical_price(dataframe),
            window=int(self.bb_period.value),
            stds=float(self.bb_std.value),
        )
        dataframe["bb_lowerband"] = bb["lower"]
        dataframe["bb_middleband"] = bb["mid"]
        dataframe["bb_upperband"] = bb["upper"]
        dataframe["bb_width"] = (dataframe["bb_upperband"] - dataframe["bb_lowerband"]) / dataframe["bb_middleband"]
        dataframe["bb_percent"] = (dataframe["close"] - dataframe["bb_lowerband"]) / (
            dataframe["bb_upperband"] - dataframe["bb_lowerband"]
        )

        # Supertrend
        dataframe["supertrend"], dataframe["st_dir"] = self._supertrend(
            dataframe,
            int(self.st_atr_period.value),
            float(self.st_multiplier.value),
        )

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Core signals: EMA regime, optionally requiring a recent crossover.
        ema_above = dataframe["ema_fast"] > dataframe["ema_slow"]
        ema_below = dataframe["ema_fast"] < dataframe["ema_slow"]
        if self.use_recent_cross_confirm.value:
            lb = int(self.cross_lookback.value)
            cross_up_recent = qtpylib.crossed_above(dataframe["ema_fast"], dataframe["ema_slow"]).rolling(
                lb, min_periods=1
            ).max() > 0
            cross_down_recent = qtpylib.crossed_below(dataframe["ema_fast"], dataframe["ema_slow"]).rolling(
                lb, min_periods=1
            ).max() > 0
            long_signal = ema_above & cross_up_recent
            short_signal = ema_below & cross_down_recent
        else:
            long_signal = ema_above
            short_signal = ema_below

        # Trend guards to avoid early counter-trend entries
        if self.use_trend_guard.value:
            trend_guard_long = dataframe["close"] > dataframe["ema_trend"]
            trend_guard_short = dataframe["close"] < dataframe["ema_trend"]
        else:
            trend_guard_long = pd.Series(True, index=dataframe.index)
            trend_guard_short = pd.Series(True, index=dataframe.index)

        # Individual filters
        st_ok_long = dataframe["st_dir"] == 1
        st_ok_short = dataframe["st_dir"] == -1
        adx_ok = dataframe["adx"] >= self.adx_threshold.value
        rsi_ok_long = (dataframe["rsi"] < self.rsi_overbought.value) & (dataframe["rsi"] > self.rsi_oversold.value)
        rsi_ok_short = (dataframe["rsi"] < self.rsi_overbought.value) & (dataframe["rsi"] > self.rsi_oversold.value)
        vol_ok = dataframe["volume"] > (dataframe["volume_ma"] * float(self.volume_mult.value))

        bb_mode = self.bb_mode.value
        if bb_mode == "avoid_extremes":
            bb_ok_long = (dataframe["bb_percent"] > 0.10) & (dataframe["bb_percent"] < 0.90)
            bb_ok_short = (dataframe["bb_percent"] > 0.10) & (dataframe["bb_percent"] < 0.90)
        elif bb_mode == "squeeze_only":
            bb_ok_long = dataframe["bb_width"] <= float(self.bb_squeeze_width.value)
            bb_ok_short = dataframe["bb_width"] <= float(self.bb_squeeze_width.value)
        elif bb_mode == "trend_position":
            bb_ok_long = dataframe["close"] > dataframe["bb_middleband"]
            bb_ok_short = dataframe["close"] < dataframe["bb_middleband"]
        else:  # wide_bands
            bb_ok_long = dataframe["bb_width"] >= float(self.bb_wide_width.value)
            bb_ok_short = dataframe["bb_width"] >= float(self.bb_wide_width.value)

        enabled_filters = 0
        score_long = pd.Series(index=dataframe.index, data=0, dtype="int64")
        score_short = pd.Series(index=dataframe.index, data=0, dtype="int64")

        if self.use_supertrend.value:
            enabled_filters += 1
            score_long += st_ok_long.astype(int)
            score_short += st_ok_short.astype(int)
        if self.use_adx_filter.value:
            enabled_filters += 1
            score_long += adx_ok.astype(int)
            score_short += adx_ok.astype(int)
        if self.use_rsi_filter.value:
            enabled_filters += 1
            score_long += rsi_ok_long.astype(int)
            score_short += rsi_ok_short.astype(int)
        if self.use_volume_filter.value:
            enabled_filters += 1
            score_long += vol_ok.astype(int)
            score_short += vol_ok.astype(int)
        if self.use_bb_filter.value:
            enabled_filters += 1
            score_long += bb_ok_long.astype(int)
            score_short += bb_ok_short.astype(int)

        required = self._required_score(enabled_filters)
        filters_pass_long = score_long >= required
        filters_pass_short = score_short >= required

        if self.require_nonzero_volume.value:
            volume_ok = dataframe["volume"] > 0
        else:
            volume_ok = pd.Series(True, index=dataframe.index)

        dataframe.loc[
            (
                volume_ok
                & long_signal
                & trend_guard_long
                & filters_pass_long
            ),
            "enter_long",
        ] = 1

        dataframe.loc[
            (
                volume_ok
                & short_signal
                & trend_guard_short
                & filters_pass_short
            ),
            "enter_short",
        ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Core crossover exits
        ema_cross_down = qtpylib.crossed_below(dataframe["ema_fast"], dataframe["ema_slow"])
        ema_cross_up = qtpylib.crossed_above(dataframe["ema_fast"], dataframe["ema_slow"])

        # Optional supertrend flips as extra exit triggers
        st_bear = dataframe["st_dir"] == -1
        st_bull = dataframe["st_dir"] == 1
        if self.use_supertrend.value:
            exit_long_cond = ema_cross_down | st_bear
            exit_short_cond = ema_cross_up | st_bull
        else:
            exit_long_cond = ema_cross_down
            exit_short_cond = ema_cross_up

        if self.require_nonzero_volume.value:
            volume_ok = dataframe["volume"] > 0
        else:
            volume_ok = pd.Series(True, index=dataframe.index)

        dataframe.loc[
            (
                volume_ok
                & exit_long_cond
            ),
            "exit_long",
        ] = 1
        dataframe.loc[
            (
                volume_ok
                & exit_short_cond
            ),
            "exit_short",
        ] = 1
        return dataframe

    def custom_stoploss(
        self,
        pair: str,
        trade: Trade,
        current_time: datetime,
        current_rate: float,
        current_profit: float,
        after_fill: bool,
        **kwargs,
    ) -> Optional[float]:
        if not self.use_atr_stoploss.value:
            return self.stoploss

        if self.dp is None:
            return self.stoploss

        df, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if df.empty:
            return self.stoploss

        last = df.iloc[-1]
        atr = last.get("atr", np.nan)
        if np.isnan(atr) or atr <= 0:
            return self.stoploss

        if trade.is_short:
            stop_price = current_rate + (float(self.atr_sl_mult.value) * atr)
            return stoploss_from_absolute(stop_price, current_rate=current_rate, is_short=True)

        stop_price = current_rate - (float(self.atr_sl_mult.value) * atr)
        return stoploss_from_absolute(stop_price, current_rate=current_rate, is_short=False)

    def custom_exit(
        self,
        pair: str,
        trade: Trade,
        current_time: datetime,
        current_rate: float,
        current_profit: float,
        **kwargs,
    ):
        if not self.use_atr_takeprofit.value or self.dp is None:
            return None

        df, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if df.empty:
            return None

        last = df.iloc[-1]
        atr = last.get("atr", np.nan)
        if np.isnan(atr) or atr <= 0:
            return None

        tp_ratio = (float(self.atr_tp_mult.value) * atr) / current_rate
        if current_profit >= tp_ratio:
            return "atr_takeprofit"

        return None

    def custom_stake_amount(
        self,
        pair: str,
        current_time: datetime,
        current_rate: float,
        proposed_stake: float,
        min_stake: Optional[float],
        max_stake: float,
        leverage: float,
        entry_tag: Optional[str],
        side: str,
        **kwargs,
    ) -> float:
        # Optional risk-based stake sizing.
        if not self.use_risk_position_size.value:
            return proposed_stake

        if self.dp is None:
            return proposed_stake

        df, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if df.empty:
            return proposed_stake

        atr = float(df.iloc[-1].get("atr", np.nan))
        if np.isnan(atr) or atr <= 0:
            return proposed_stake

        stop_distance_ratio = (float(self.atr_sl_mult.value) * atr) / current_rate
        if stop_distance_ratio <= 0:
            return proposed_stake

        # Approximate wallet size in stake currency.
        wallet_total = proposed_stake
        if self.wallets:
            try:
                wallet_total = max(self.wallets.get_total_stake_amount(), proposed_stake)
            except Exception:
                wallet_total = proposed_stake

        risk_amount = wallet_total * (float(self.risk_per_trade.value) / 100.0)
        stake = risk_amount / stop_distance_ratio

        if min_stake is not None:
            stake = max(stake, min_stake)
        stake = min(stake, max_stake)
        return float(stake)

