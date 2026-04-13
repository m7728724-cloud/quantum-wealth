"""Quantum Signal Brain — Multi-indicator confluence engine for Binary Options"""
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# ============================================
# Technical Indicator Calculations
# ============================================

def calc_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Calculate Relative Strength Index"""
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calc_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    """Calculate MACD, Signal line, and Histogram"""
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def calc_bollinger(series: pd.Series, period: int = 20, std_dev: float = 2.0):
    """Calculate Bollinger Bands"""
    sma = series.rolling(window=period).mean()
    std = series.rolling(window=period).std()
    upper = sma + (std * std_dev)
    lower = sma - (std * std_dev)
    return upper, sma, lower


def calc_ema(series: pd.Series, period: int) -> pd.Series:
    """Calculate Exponential Moving Average"""
    return series.ewm(span=period, adjust=False).mean()


def calc_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Calculate Average True Range"""
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(window=period).mean()


def calc_stochastic(high: pd.Series, low: pd.Series, close: pd.Series,
                     k_period: int = 14, d_period: int = 3):
    """Calculate Stochastic Oscillator %K and %D"""
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()
    k = 100 * (close - lowest_low) / (highest_high - lowest_low).replace(0, np.nan)
    d = k.rolling(window=d_period).mean()
    return k, d


# ============================================
# Signal Analysis Engine
# ============================================

def analyze_pair(df: pd.DataFrame, symbol: str) -> Optional[Dict[str, Any]]:
    """Analyze a single forex pair and return signal if confluence is met.

    Returns None if no signal, or a dict with signal details.
    """
    if df is None or len(df) < 50:
        return None

    try:
        close = df["Close"].squeeze() if isinstance(df["Close"], pd.DataFrame) else df["Close"]
        high = df["High"].squeeze() if isinstance(df["High"], pd.DataFrame) else df["High"]
        low = df["Low"].squeeze() if isinstance(df["Low"], pd.DataFrame) else df["Low"]

        # Calculate all indicators
        rsi = calc_rsi(close)
        macd_line, macd_signal, macd_hist = calc_macd(close)
        bb_upper, bb_mid, bb_lower = calc_bollinger(close)
        ema9 = calc_ema(close, 9)
        ema21 = calc_ema(close, 21)
        atr = calc_atr(high, low, close)
        stoch_k, stoch_d = calc_stochastic(high, low, close)

        # Get latest values
        i = -1  # latest candle
        current_close = float(close.iloc[i])
        current_rsi = float(rsi.iloc[i]) if not pd.isna(rsi.iloc[i]) else 50
        current_macd = float(macd_line.iloc[i]) if not pd.isna(macd_line.iloc[i]) else 0
        current_macd_signal = float(macd_signal.iloc[i]) if not pd.isna(macd_signal.iloc[i]) else 0
        prev_macd = float(macd_line.iloc[i-1]) if not pd.isna(macd_line.iloc[i-1]) else 0
        prev_macd_signal = float(macd_signal.iloc[i-1]) if not pd.isna(macd_signal.iloc[i-1]) else 0
        current_bb_upper = float(bb_upper.iloc[i]) if not pd.isna(bb_upper.iloc[i]) else current_close
        current_bb_lower = float(bb_lower.iloc[i]) if not pd.isna(bb_lower.iloc[i]) else current_close
        current_ema9 = float(ema9.iloc[i]) if not pd.isna(ema9.iloc[i]) else current_close
        current_ema21 = float(ema21.iloc[i]) if not pd.isna(ema21.iloc[i]) else current_close
        current_atr = float(atr.iloc[i]) if not pd.isna(atr.iloc[i]) else 0
        avg_atr = float(atr.mean()) if not pd.isna(atr.mean()) else 0
        current_stoch_k = float(stoch_k.iloc[i]) if not pd.isna(stoch_k.iloc[i]) else 50
        current_stoch_d = float(stoch_d.iloc[i]) if not pd.isna(stoch_d.iloc[i]) else 50
        prev_stoch_k = float(stoch_k.iloc[i-1]) if not pd.isna(stoch_k.iloc[i-1]) else 50
        prev_stoch_d = float(stoch_d.iloc[i-1]) if not pd.isna(stoch_d.iloc[i-1]) else 50

        # ============================================
        # CALL indicators
        # ============================================
        call_indicators = []
        put_indicators = []

        # 1. RSI
        if current_rsi < 30:
            call_indicators.append({"name": "RSI", "value": round(current_rsi, 1), "reason": f"Перепроданность (RSI={round(current_rsi, 1)})"})
        elif current_rsi > 70:
            put_indicators.append({"name": "RSI", "value": round(current_rsi, 1), "reason": f"Перекупленность (RSI={round(current_rsi, 1)})"})

        # 2. MACD crossover
        macd_cross_up = prev_macd <= prev_macd_signal and current_macd > current_macd_signal
        macd_cross_down = prev_macd >= prev_macd_signal and current_macd < current_macd_signal
        if macd_cross_up:
            call_indicators.append({"name": "MACD", "value": round(current_macd, 6), "reason": "MACD пересёк сигнальную линию снизу вверх"})
        elif macd_cross_down:
            put_indicators.append({"name": "MACD", "value": round(current_macd, 6), "reason": "MACD пересёк сигнальную линию сверху вниз"})

        # 3. Bollinger Bands
        bb_width = current_bb_upper - current_bb_lower
        if bb_width > 0:
            if current_close <= current_bb_lower + bb_width * 0.05:
                call_indicators.append({"name": "Bollinger", "value": round(current_close, 5), "reason": "Цена у нижней полосы Боллинджера"})
            elif current_close >= current_bb_upper - bb_width * 0.05:
                put_indicators.append({"name": "Bollinger", "value": round(current_close, 5), "reason": "Цена у верхней полосы Боллинджера"})

        # 4. EMA Cross (trend direction)
        if current_ema9 > current_ema21:
            call_indicators.append({"name": "EMA Cross", "value": f"EMA9={round(current_ema9, 5)}", "reason": "EMA9 > EMA21 — бычий тренд"})
        elif current_ema9 < current_ema21:
            put_indicators.append({"name": "EMA Cross", "value": f"EMA9={round(current_ema9, 5)}", "reason": "EMA9 < EMA21 — медвежий тренд"})

        # 5. ATR filter (volatility must be sufficient)
        atr_ok = current_atr > avg_atr * 0.7 if avg_atr > 0 else True
        if atr_ok:
            call_indicators.append({"name": "ATR", "value": round(current_atr, 6), "reason": f"Волатильность достаточная (ATR={round(current_atr, 6)})"})
            put_indicators.append({"name": "ATR", "value": round(current_atr, 6), "reason": f"Волатильность достаточная (ATR={round(current_atr, 6)})"})

        # 6. Stochastic
        stoch_cross_up = prev_stoch_k <= prev_stoch_d and current_stoch_k > current_stoch_d
        stoch_cross_down = prev_stoch_k >= prev_stoch_d and current_stoch_k < current_stoch_d
        if current_stoch_k < 20 and stoch_cross_up:
            call_indicators.append({"name": "Stochastic", "value": round(current_stoch_k, 1), "reason": f"Stoch перепродан + пересечение вверх (%K={round(current_stoch_k, 1)})"})
        elif current_stoch_k > 80 and stoch_cross_down:
            put_indicators.append({"name": "Stochastic", "value": round(current_stoch_k, 1), "reason": f"Stoch перекуплен + пересечение вниз (%K={round(current_stoch_k, 1)})"})

        # ============================================
        # Confluence Decision
        # ============================================
        call_score = len(call_indicators)
        put_score = len(put_indicators)

        # Need minimum 3 indicators to agree
        if call_score >= 3 and call_score > put_score:
            confidence = min(95, 50 + call_score * 8)
            strength = "STRONG" if call_score >= 4 else "MODERATE"
            return {
                "symbol": symbol,
                "direction": "CALL",
                "confluence_score": call_score,
                "max_possible": 6,
                "confidence": confidence,
                "strength": strength,
                "indicators_triggered": call_indicators,
                "price": current_close,
                "rsi": round(current_rsi, 1),
                "macd": round(current_macd, 6),
                "stochastic_k": round(current_stoch_k, 1),
                "atr": round(current_atr, 6),
                "timestamp": datetime.now().isoformat()
            }
        elif put_score >= 3 and put_score > call_score:
            confidence = min(95, 50 + put_score * 8)
            strength = "STRONG" if put_score >= 4 else "MODERATE"
            return {
                "symbol": symbol,
                "direction": "PUT",
                "confluence_score": put_score,
                "max_possible": 6,
                "confidence": confidence,
                "strength": strength,
                "indicators_triggered": put_indicators,
                "price": current_close,
                "rsi": round(current_rsi, 1),
                "macd": round(current_macd, 6),
                "stochastic_k": round(current_stoch_k, 1),
                "atr": round(current_atr, 6),
                "timestamp": datetime.now().isoformat()
            }

        return None  # No confluence — no signal

    except Exception as e:
        logger.error(f"Error analyzing {symbol}: {e}")
        return None


def scan_all_pairs(price_data: Dict[str, pd.DataFrame]) -> List[Dict[str, Any]]:
    """Scan all pairs and return list of signals that passed confluence."""
    signals = []
    for symbol, df in price_data.items():
        result = analyze_pair(df, symbol)
        if result is not None:
            signals.append(result)
    return signals


# ============================================
# Performance Tracking
# ============================================

def calculate_indicator_performance(trades: List[Dict]) -> Dict[str, Any]:
    """Analyze which indicators perform best based on trade history."""
    if not trades:
        return {"message": "No trade data yet for performance analysis"}

    stats = {}
    for trade in trades:
        result = trade.get("result", "PENDING")
        if result not in ("WIN", "LOSS"):
            continue

        indicators = trade.get("indicators_triggered", [])
        for ind in indicators:
            name = ind if isinstance(ind, str) else ind.get("name", "unknown")
            if name not in stats:
                stats[name] = {"wins": 0, "losses": 0, "total": 0}
            stats[name]["total"] += 1
            if result == "WIN":
                stats[name]["wins"] += 1
            else:
                stats[name]["losses"] += 1

    # Calculate win rates
    performance = {}
    for name, data in stats.items():
        wr = round(data["wins"] / data["total"] * 100, 1) if data["total"] > 0 else 0
        performance[name] = {**data, "win_rate": wr}

    return performance
