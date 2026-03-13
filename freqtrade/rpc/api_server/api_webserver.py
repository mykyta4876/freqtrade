import logging

from fastapi import APIRouter, Depends

from datetime import UTC, datetime, timedelta

from pandas import DataFrame

from freqtrade.data.history.datahandlers import get_datahandler
from freqtrade.enums import CandleType, TradingMode
from freqtrade.exchange.exchange_utils_timeframe import timeframe_to_seconds
from freqtrade.rpc.api_server.api_schemas import (
    AvailablePairs,
    DataCheckResult,
    DataGap,
    ExchangeListResponse,
    FreqAIModelListResponse,
    HyperoptLossListResponse,
    StrategyListResponse,
)
from freqtrade.rpc.api_server.deps import get_config
from freqtrade.util import dt_from_ts


logger = logging.getLogger(__name__)

# Private API, protected by authentication and webserver_mode dependency
router = APIRouter()


@router.get("/strategies", response_model=StrategyListResponse, tags=["Strategy"])
def list_strategies(config=Depends(get_config)):
    from freqtrade.resolvers.strategy_resolver import StrategyResolver

    strategies = StrategyResolver.search_all_objects(
        config, False, config.get("recursive_strategy_search", False)
    )
    strategies = sorted(strategies, key=lambda x: x["name"])

    return {"strategies": [x["name"] for x in strategies]}


@router.get("/exchanges", response_model=ExchangeListResponse, tags=[])
def list_exchanges(config=Depends(get_config)):
    from freqtrade.exchange import list_available_exchanges

    exchanges = list_available_exchanges(config)
    return {
        "exchanges": exchanges,
    }


@router.get("/hyperoptloss", response_model=HyperoptLossListResponse, tags=["Hyperopt"])
def list_hyperoptloss(
    config=Depends(get_config),
):
    import textwrap

    from freqtrade.resolvers.hyperopt_resolver import HyperOptLossResolver

    loss_functions = HyperOptLossResolver.search_all_objects(config, False)
    loss_functions = sorted(loss_functions, key=lambda x: x["name"])

    return {
        "loss_functions": [
            {
                "name": x["name"],
                "description": textwrap.dedent((x["class"].__doc__ or "").strip()),
            }
            for x in loss_functions
        ]
    }


@router.get("/freqaimodels", response_model=FreqAIModelListResponse, tags=["FreqAI"])
def list_freqaimodels(config=Depends(get_config)):
    from freqtrade.resolvers.freqaimodel_resolver import FreqaiModelResolver

    models = FreqaiModelResolver.search_all_objects(config, False)
    models = sorted(models, key=lambda x: x["name"])

    return {"freqaimodels": [x["name"] for x in models]}


@router.get(
    "/available_pairs", response_model=AvailablePairs, tags=["Candle data", "Download-data"]
)
def list_available_pairs(
    timeframe: str | None = None,
    stake_currency: str | None = None,
    candletype: CandleType | None = None,
    config=Depends(get_config),
):
    dh = get_datahandler(config["datadir"], config.get("dataformat_ohlcv"))
    trading_mode: TradingMode = config.get("trading_mode", TradingMode.SPOT)
    pair_interval = dh.ohlcv_get_available_data(config["datadir"], trading_mode)

    if timeframe:
        pair_interval = [pair for pair in pair_interval if pair[1] == timeframe]
    if stake_currency:
        pair_interval = [pair for pair in pair_interval if pair[0].endswith(stake_currency)]
    if candletype:
        pair_interval = [pair for pair in pair_interval if pair[2] == candletype]
    else:
        candle_type = CandleType.get_default(trading_mode)
        pair_interval = [pair for pair in pair_interval if pair[2] == candle_type]

    pair_interval = sorted(pair_interval, key=lambda x: x[0])

    pairs = list({x[0] for x in pair_interval})
    pairs.sort()
    result = {
        "length": len(pairs),
        "pairs": pairs,
        "pair_interval": pair_interval,
    }
    return result


@router.get(
    "/check_data", response_model=DataCheckResult, tags=["Candle data", "Download-data"]
)
def check_data_by_volume(
    pair: str,
    timeframe: str,
    timerange: str | None = None,
    candletype: CandleType | None = None,
    config=Depends(get_config),
):
    """
    Check data completeness by examining volume.
    Identifies missing candles and zero-volume candles that may indicate data gaps.
    
    :param pair: Trading pair (e.g., BTC/USDT)
    :param timeframe: Timeframe (e.g., 5m)
    :param timerange: Optional timerange to check (e.g., 20260201-20260301)
    :param candletype: Candle type (defaults to trading mode default)
    :param config: Freqtrade config
    :return: DataCheckResult with completeness information
    """
    from freqtrade.configuration.timerange import TimeRange

    dh = get_datahandler(config["datadir"], config.get("dataformat_ohlcv"))
    trading_mode: TradingMode = config.get("trading_mode", TradingMode.SPOT)
    
    if candletype is None:
        candletype = CandleType.get_default(trading_mode)

    # Parse timerange if provided
    timerange_obj: TimeRange | None = None
    if timerange:
        try:
            timerange_obj = TimeRange.parse_timerange(timerange)
        except Exception as e:
            logger.warning(f"Failed to parse timerange {timerange}: {e}")
            timerange_obj = None

    # Load OHLCV data
    try:
        dataframe = dh.ohlcv_load(
            pair=pair,
            timeframe=timeframe,
            candle_type=candletype,
            timerange=timerange_obj,
            fill_missing=False,  # Don't fill missing - we want to detect gaps
            drop_incomplete=False,
        )
    except Exception as e:
        logger.error(f"Error loading data for {pair}/{timeframe}: {e}")
        return DataCheckResult(
            pair=pair,
            timeframe=timeframe,
            timerange=timerange,
            data_start=None,
            data_end=None,
            total_candles=0,
            expected_candles=None,
            missing_candles=0,
            zero_volume_candles=0,
            completeness_percent=0.0,
            gaps=[],
            status="empty",
        )

    # Check if data is empty
    if dataframe.empty:
        return DataCheckResult(
            pair=pair,
            timeframe=timeframe,
            timerange=timerange,
            data_start=None,
            data_end=None,
            total_candles=0,
            expected_candles=None,
            missing_candles=0,
            zero_volume_candles=0,
            completeness_percent=0.0,
            gaps=[],
            status="empty",
        )

    # Get data range
    data_start = dataframe["date"].iloc[0]
    data_end = dataframe["date"].iloc[-1]
    
    # Calculate expected candles if timerange is provided
    expected_candles: int | None = None
    if timerange_obj and timerange_obj.startts and timerange_obj.stopts:
        timeframe_secs = timeframe_to_seconds(timeframe)
        duration_secs = timerange_obj.stopts - timerange_obj.startts
        expected_candles = int(duration_secs / timeframe_secs)
    
    # Count zero volume candles
    zero_volume_mask = (dataframe["volume"] == 0) | (dataframe["volume"].isna())
    zero_volume_candles = int(zero_volume_mask.sum())

    # Detect gaps (missing candles)
    gaps: list[DataGap] = []
    missing_candles = 0
    
    if len(dataframe) > 1:
        timeframe_secs = timeframe_to_seconds(timeframe)
        expected_interval = timedelta(seconds=timeframe_secs)
        
        # Check for gaps between consecutive candles
        for i in range(len(dataframe) - 1):
            current_time = dataframe["date"].iloc[i]
            next_time = dataframe["date"].iloc[i + 1]
            time_diff = next_time - current_time
            
            # If gap is more than 1.5x the expected interval, it's a gap
            if time_diff > expected_interval * 1.5:
                gap_start = current_time
                gap_end = next_time
                gap_duration = time_diff.total_seconds()
                candles_in_gap = int(gap_duration / timeframe_secs) - 1
                
                gaps.append(
                    DataGap(
                        start=gap_start.strftime("%Y-%m-%d %H:%M:%S"),
                        end=gap_end.strftime("%Y-%m-%d %H:%M:%S"),
                        missing_candles=candles_in_gap,
                        zero_volume_candles=0,  # Gaps don't have volume
                    )
                )
                missing_candles += candles_in_gap
        
        # Check for missing data at the start if timerange is specified
        if timerange_obj and timerange_obj.startts:
            timerange_start = dt_from_ts(timerange_obj.startts)
            if data_start > timerange_start:
                gap_duration = (data_start - timerange_start).total_seconds()
                candles_in_gap = int(gap_duration / timeframe_secs)
                if candles_in_gap > 0:
                    gaps.insert(
                        0,
                        DataGap(
                            start=timerange_start.strftime("%Y-%m-%d %H:%M:%S"),
                            end=data_start.strftime("%Y-%m-%d %H:%M:%S"),
                            missing_candles=candles_in_gap,
                            zero_volume_candles=0,
                        ),
                    )
                    missing_candles += candles_in_gap
        
        # Check for missing data at the end if timerange is specified
        if timerange_obj and timerange_obj.stopts:
            timerange_end = dt_from_ts(timerange_obj.stopts)
            if data_end < timerange_end:
                gap_duration = (timerange_end - data_end).total_seconds()
                candles_in_gap = int(gap_duration / timeframe_secs)
                if candles_in_gap > 0:
                    gaps.append(
                        DataGap(
                            start=data_end.strftime("%Y-%m-%d %H:%M:%S"),
                            end=timerange_end.strftime("%Y-%m-%d %H:%M:%S"),
                            missing_candles=candles_in_gap,
                            zero_volume_candles=0,
                        )
                    )
                    missing_candles += candles_in_gap

    # Calculate completeness percentage
    total_candles = len(dataframe)
    if expected_candles and expected_candles > 0:
        completeness_percent = (total_candles / expected_candles) * 100.0
    else:
        completeness_percent = 100.0 if missing_candles == 0 else 0.0

    # Determine status
    if total_candles == 0:
        status = "empty"
    elif missing_candles > 0 or (expected_candles and total_candles < expected_candles * 0.95):
        status = "incomplete"
    elif zero_volume_candles > total_candles * 0.1:  # More than 10% zero volume
        status = "incomplete"
    else:
        status = "complete"

    return DataCheckResult(
        pair=pair,
        timeframe=timeframe,
        timerange=timerange,
        data_start=data_start.strftime("%Y-%m-%d %H:%M:%S") if not dataframe.empty else None,
        data_end=data_end.strftime("%Y-%m-%d %H:%M:%S") if not dataframe.empty else None,
        total_candles=total_candles,
        expected_candles=expected_candles,
        missing_candles=missing_candles,
        zero_volume_candles=zero_volume_candles,
        completeness_percent=round(completeness_percent, 2),
        gaps=gaps,
        status=status,
    )
