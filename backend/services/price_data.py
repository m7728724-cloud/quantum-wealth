"""Price Data Service — Forex candle data fetcher via yfinance"""
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, List

import pandas as pd

logger = logging.getLogger(__name__)

# Ticker mapping: our symbol → yfinance ticker
FOREX_TICKERS = {
    "EURUSD": "EURUSD=X",
    "USDJPY": "USDJPY=X",
    "AUDUSD": "AUDUSD=X",
    "AUDJPY": "AUDJPY=X",
    "EURJPY": "EURJPY=X",
    "USDCAD": "USDCAD=X",
    "GBPUSD": "GBPUSD=X",
    "GBPJPY": "GBPJPY=X",
    "EURGBP": "EURGBP=X",
    "NZDUSD": "NZDUSD=X",
    "AUDCAD": "AUDCAD=X",
    "AUDCHF": "AUDCHF=X",
    "AUDNZD": "AUDNZD=X",
    "CADJPY": "CADJPY=X",
    "EURAUD": "EURAUD=X",
    "EURCAD": "EURCAD=X",
    "EURCHF": "EURCHF=X",
    "GBPAUD": "GBPAUD=X",
    "GBPCHF": "GBPCHF=X",
    "GBPNZD": "GBPNZD=X",
    "NZDJPY": "NZDJPY=X",
    "USDCHF": "USDCHF=X",
}

# In-memory cache: {symbol: {"df": DataFrame, "updated_at": timestamp}}
_cache: Dict[str, Dict] = {}
CACHE_TTL = 120  # 2 minutes


def get_supported_symbols() -> List[str]:
    """Return list of all supported symbols"""
    return list(FOREX_TICKERS.keys())


def fetch_candles(symbol: str, interval: str = "1m", period: str = "2d") -> Optional[pd.DataFrame]:
    """Fetch OHLCV candle data for a forex pair.

    Args:
        symbol: e.g. "EURUSD"
        interval: candle interval ("1m", "5m", "15m")
        period: how far back ("1d", "2d", "5d")

    Returns:
        DataFrame with columns: Open, High, Low, Close, Volume
    """
    import yfinance as yf

    ticker = FOREX_TICKERS.get(symbol)
    if not ticker:
        logger.warning(f"Unknown symbol: {symbol}")
        return None

    # Check cache
    now = time.time()
    cached = _cache.get(symbol)
    if cached and (now - cached["updated_at"]) < CACHE_TTL:
        return cached["df"]

    try:
        data = yf.download(
            ticker,
            period=period,
            interval=interval,
            auto_adjust=True,
            progress=False,
        )

        if data is None or data.empty:
            logger.warning(f"No data returned for {symbol}")
            return None

        # Flatten multi-level columns if present (yfinance sometimes returns multi-index)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # Cache it
        _cache[symbol] = {"df": data, "updated_at": now}
        logger.info(f"Fetched {len(data)} candles for {symbol}")
        return data

    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {e}")
        return None


def fetch_multi(symbols: List[str], interval: str = "1m") -> Dict[str, pd.DataFrame]:
    """Fetch candle data for multiple symbols"""
    results = {}
    for sym in symbols:
        df = fetch_candles(sym, interval=interval)
        if df is not None and not df.empty:
            results[sym] = df
    return results


def get_current_price(symbol: str) -> Optional[float]:
    """Get the latest close price for a symbol"""
    df = fetch_candles(symbol)
    if df is not None and not df.empty:
        return float(df["Close"].iloc[-1])
    return None


def clear_cache():
    """Clear all cached data"""
    global _cache
    _cache = {}
