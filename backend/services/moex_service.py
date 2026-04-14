"""MOEX ISS API Service - ISIN Resolution & Market Data"""
import requests
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Cache for ISIN lookups (in-memory, refreshes periodically)
_isin_cache: Dict[str, Dict] = {}
_cache_ttl = timedelta(hours=6)
_cache_timestamps: Dict[str, datetime] = {}

MOEX_BASE = "https://iss.moex.com/iss"

# Known liquidity fund tickers
LIQUIDITY_FUND_SECIDS = {"LQDT", "SBMM", "VTBM", "AKMM", "TMON"}


def resolve_isin(isin: str) -> Optional[Dict[str, Any]]:
    """Resolve ISIN code to human-readable asset information via MOEX ISS API"""
    isin = isin.strip().upper()
    
    # Check cache
    if isin in _isin_cache:
        cache_time = _cache_timestamps.get(isin)
        if cache_time and datetime.now() - cache_time < _cache_ttl:
            logger.info(f"Cache hit for ISIN {isin}")
            return _isin_cache[isin]
    
    try:
        url = f"{MOEX_BASE}/securities.json"
        params = {
            "q": isin,
            "iss.meta": "off",
            "iss.only": "securities",
            "securities.columns": "secid,shortname,name,isin,type,group,primary_boardid",
            "limit": 10
        }
        
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        
        securities = data.get("securities", {}).get("data", [])
        columns = data.get("securities", {}).get("columns", [])
        
        if not securities:
            logger.warning(f"No results for ISIN {isin}")
            return None
        
        # Find exact ISIN match first
        for sec in securities:
            mapped = dict(zip(columns, sec))
            if mapped.get("isin") == isin:
                result = _build_result(mapped, isin)
                _cache_result(isin, result)
                return result
        
        # Use first result as best match
        mapped = dict(zip(columns, securities[0]))
        result = _build_result(mapped, isin)
        _cache_result(isin, result)
        return result
        
    except requests.exceptions.Timeout:
        logger.error(f"MOEX API timeout for ISIN {isin}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"MOEX API error for ISIN {isin}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error resolving ISIN {isin}: {e}")
        return None


def _build_result(mapped: Dict, isin: str) -> Dict[str, Any]:
    """Build standardized result from MOEX response"""
    secid = mapped.get("secid", "")
    group = mapped.get("group", "")
    sec_type = mapped.get("type", "")
    
    # Determine asset class
    asset_class = _classify_asset(secid, group, sec_type)
    is_liquidity = secid in LIQUIDITY_FUND_SECIDS or asset_class == "liquidity_fund"
    
    return {
        "isin": isin,
        "secid": secid,
        "shortname": mapped.get("shortname", "Unknown"),
        "fullname": mapped.get("name", "Unknown"),
        "type": sec_type,
        "group": group,
        "primary_boardid": mapped.get("primary_boardid", ""),
        "asset_class": asset_class,
        "is_liquidity_fund": is_liquidity
    }


def _classify_asset(secid: str, group: str, sec_type: str) -> str:
    """Classify asset into categories"""
    if secid in LIQUIDITY_FUND_SECIDS:
        return "liquidity_fund"
    
    group_lower = (group or "").lower()
    type_lower = (sec_type or "").lower()
    
    if "share" in group_lower or "share" in type_lower:
        return "stock"
    elif "bond" in group_lower or "bond" in type_lower or "ofz" in type_lower:
        return "bond"
    elif "etf" in group_lower or "ppif" in group_lower:
        return "etf"
    elif "fund" in group_lower or "money_market" in type_lower:
        return "liquidity_fund"
    
    return "unknown"


def _cache_result(isin: str, result: Dict):
    """Cache ISIN resolution result"""
    _isin_cache[isin] = result
    _cache_timestamps[isin] = datetime.now()


def get_security_market_data(secid: str) -> Optional[Dict]:
    """Get current market data for a security by SECID"""
    try:
        url = f"{MOEX_BASE}/engines/stock/markets/shares/securities/{secid}.json"
        params = {
            "iss.meta": "off",
            "iss.only": "marketdata",
            "marketdata.columns": "SECID,LAST,CHANGE,LASTTOPREVPRICE,VOLTODAY,VALTODAY"
        }
        
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        md = data.get("marketdata", {}).get("data", [])
        cols = data.get("marketdata", {}).get("columns", [])
        
        if md:
            for row in md:
                mapped = dict(zip(cols, row))
                if mapped.get("LAST") is not None:
                    return mapped
        return None
    except Exception as e:
        logger.error(f"Market data error for {secid}: {e}")
        return None


def get_top_moex_stocks() -> List[Dict[str, Any]]:
    """Fetch snapshot for popular MOEX stocks."""
    tickers = [
        "SBER", "LKOH", "GAZP", "NVTK", "ROSN", "YNDX", "MGNT", "GMKN", "TATN", "SNGS",
        "VTBR", "ALRS", "MAGN", "CHMF", "NLMK", "PHOR", "AFKS", "OZON", "FIVE", "PIKK"
    ]
    securities = ",".join(tickers)
    url = (
        f"{MOEX_BASE}/engines/stock/markets/shares/boards/TQBR/securities.json"
        f"?securities={securities}&iss.meta=off&iss.only=marketdata,securities"
        f"&marketdata.columns=SECID,LAST,CHANGE,LASTTOPREVPRICE,VOLUME"
        f"&securities.columns=SECID,SHORTNAME"
    )
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        payload = resp.json()
        sec_rows = payload.get("securities", {}).get("data", [])
        sec_cols = payload.get("securities", {}).get("columns", [])
        md_rows = payload.get("marketdata", {}).get("data", [])
        md_cols = payload.get("marketdata", {}).get("columns", [])
        names = {row[0]: dict(zip(sec_cols, row)).get("SHORTNAME", row[0]) for row in sec_rows if row}
        result = []
        for row in md_rows:
            mapped = dict(zip(md_cols, row))
            secid = mapped.get("SECID")
            if not secid:
                continue
            result.append({
                "secid": secid,
                "name": names.get(secid, secid),
                "price": mapped.get("LAST"),
                "change_pct": mapped.get("LASTTOPREVPRICE"),
                "volume": mapped.get("VOLUME"),
            })
        return result
    except Exception as e:
        logger.error(f"Failed to fetch top MOEX stocks: {e}")
        return []


def get_top_moex_bonds() -> List[Dict[str, Any]]:
    """Fetch snapshot for major OFZ bonds."""
    isin_list = ["SU26238RMFS4", "SU26240RMFS0", "SU26233RMFS5", "SU26226RMFS0"]
    securities = ",".join(isin_list)
    url = (
        f"{MOEX_BASE}/engines/stock/markets/bonds/boards/TQOB/securities.json"
        f"?securities={securities}&iss.meta=off&iss.only=marketdata,securities"
        f"&marketdata.columns=SECID,LAST,YIELDATWAPRICE,YIELD,CHANGE"
        f"&securities.columns=SECID,SHORTNAME,COUPONPERCENT,YIELDATPREVWAPRICE"
    )
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        payload = resp.json()
        sec_rows = payload.get("securities", {}).get("data", [])
        sec_cols = payload.get("securities", {}).get("columns", [])
        md_rows = payload.get("marketdata", {}).get("data", [])
        md_cols = payload.get("marketdata", {}).get("columns", [])

        sec_map = {}
        for row in sec_rows:
            mapped = dict(zip(sec_cols, row))
            secid = mapped.get("SECID")
            if secid:
                sec_map[secid] = mapped

        result = []
        for row in md_rows:
            mapped = dict(zip(md_cols, row))
            secid = mapped.get("SECID")
            if not secid:
                continue
            s = sec_map.get(secid, {})
            yield_pct = mapped.get("YIELDATWAPRICE") or mapped.get("YIELD") or s.get("YIELDATPREVWAPRICE")
            result.append({
                "secid": secid,
                "name": s.get("SHORTNAME", secid),
                "price": mapped.get("LAST"),
                "coupon_pct": s.get("COUPONPERCENT"),
                "yield_pct": yield_pct,
            })
        return result
    except Exception as e:
        logger.error(f"Failed to fetch top MOEX bonds: {e}")
        return []
