"""Tinkoff Investments Portfolio Sync Service"""
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


def _get_token(explicit_token: Optional[str] = None):
    return explicit_token or os.environ.get("TINKOFF_TOKEN", "")


def sync_portfolio(db, token: Optional[str] = None, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Fetch portfolio from Tinkoff and sync to MongoDB holdings collection."""
    token = _get_token(token)
    if not token:
        return {"error": "TINKOFF_TOKEN not configured", "holdings": []}

    try:
        # Try tinvest (v3) first, then tinkoff_invest (v1)
        return _sync_via_tinvest(db, token, user_id=user_id)
    except Exception as e1:
        logger.warning(f"tinvest failed: {e1}, trying tinkoff_invest...")
        try:
            return _sync_via_tinkoff_invest(db, token, user_id=user_id)
        except Exception as e2:
            logger.error(f"Both methods failed: tinvest={e1}, tinkoff_invest={e2}")
            return _sync_via_rest_api(db, token, user_id=user_id)


def _sync_via_rest_api(db, token: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Fallback: use Tinkoff REST API directly via httpx"""
    import httpx

    base_url = "https://invest-public-api.tinkoff.ru/rest"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            # Get accounts
            resp = client.post(f"{base_url}/tinkoff.public.invest.api.contract.v1.UsersService/GetAccounts",
                               headers=headers, json={})
            resp.raise_for_status()
            accounts_data = resp.json()
            accounts = accounts_data.get("accounts", [])

            if not accounts:
                return {"error": "No Tinkoff accounts found", "holdings": []}

            account_id = accounts[0]["id"]
            logger.info(f"Tinkoff account: {account_id}")

            # Get portfolio
            resp = client.post(
                f"{base_url}/tinkoff.public.invest.api.contract.v1.OperationsService/GetPortfolio",
                headers=headers,
                json={"accountId": account_id, "currency": "RUB"}
            )
            resp.raise_for_status()
            portfolio = resp.json()

            synced = []
            positions = portfolio.get("positions", [])

            for pos in positions:
                figi = pos.get("figi", "")
                instrument_type = pos.get("instrumentType", "unknown")

                # Skip currency positions
                if instrument_type == "currency":
                    continue

                quantity = _parse_quotation(pos.get("quantity", {}))
                avg_price = _parse_money(pos.get("averagePositionPrice", {}))
                current_price = _parse_money(pos.get("currentPrice", {}))

                if quantity == 0:
                    continue

                # Get instrument info
                ticker, name, isin_val = _resolve_instrument_rest(client, headers, base_url, figi, instrument_type)

                # Detect liquidity funds
                is_liq = ticker.upper() in ("LQDT", "SBMM", "VTBM", "TMON", "AMNR") if ticker else False
                asset_class = "liquidity_fund" if is_liq else _map_asset_class(instrument_type)

                holding = {
                    "user_id": user_id,
                    "isin": isin_val or figi,
                    "secid": ticker or figi,
                    "shortname": name or ticker or figi,
                    "fullname": name or ticker or figi,
                    "asset_class": asset_class,
                    "quantity": quantity,
                    "buy_price": avg_price,
                    "current_price": current_price,
                    "is_liquidity_fund": is_liq,
                    "source": "tinkoff",
                    "figi": figi,
                    "synced_at": datetime.now().isoformat(),
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                }

                db.holdings.update_one(
                    {"figi": figi, "user_id": user_id},
                    {"$set": holding},
                    upsert=True
                )
                synced.append(holding)

            total_value = _parse_money(portfolio.get("totalAmountPortfolio", {}))

            return {
                "status": "success",
                "account_id": account_id,
                "holdings_synced": len(synced),
                "total_portfolio_value": total_value,
                "currency": "RUB",
                "synced_at": datetime.now().isoformat(),
                "holdings": _serialize_holdings(synced)
            }

    except Exception as e:
        logger.error(f"Tinkoff REST API error: {e}")
        return {"error": str(e), "holdings": []}


def _resolve_instrument_rest(client, headers, base_url, figi, instrument_type):
    """Resolve instrument details via REST API"""
    try:
        service = {
            "share": "ShareBy",
            "bond": "BondBy",
            "etf": "EtfBy",
        }.get(instrument_type, "ShareBy")

        resp = client.post(
            f"{base_url}/tinkoff.public.invest.api.contract.v1.InstrumentsService/{service}",
            headers=headers,
            json={"idType": "INSTRUMENT_ID_TYPE_FIGI", "id": figi}
        )
        if resp.status_code == 200:
            data = resp.json()
            inst = data.get("instrument", {})
            return (
                inst.get("ticker", figi),
                inst.get("name", ""),
                inst.get("isin", "")
            )
    except Exception:
        pass
    return (figi, figi, "")


def _sync_via_tinvest(db, token, user_id: Optional[str] = None):
    """Try using tinvest package"""
    import tinvest
    tink = tinvest.SyncClient(token)
    accounts = tink.get_accounts()
    # This will fail if pydantic-settings is not installed
    raise ImportError("tinvest requires pydantic-settings")


def _sync_via_tinkoff_invest(db, token, user_id: Optional[str] = None):
    """Try using tinkoff_invest package"""
    raise ImportError("tinkoff_invest v1 has incompatible API - using REST fallback")


def get_tinkoff_status(token: Optional[str] = None) -> Dict[str, Any]:
    """Check if Tinkoff connection is configured and working"""
    token = _get_token(token)
    if not token:
        return {"connected": False, "reason": "TINKOFF_TOKEN not set"}

    try:
        import httpx
        base_url = "https://invest-public-api.tinkoff.ru/rest"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(
                f"{base_url}/tinkoff.public.invest.api.contract.v1.UsersService/GetAccounts",
                headers=headers, json={}
            )
            if resp.status_code == 200:
                data = resp.json()
                accounts = data.get("accounts", [])
                return {
                    "connected": True,
                    "accounts": len(accounts),
                    "account_id": accounts[0]["id"] if accounts else None
                }
            else:
                return {"connected": False, "reason": f"HTTP {resp.status_code}: {resp.text[:200]}"}
    except Exception as e:
        return {"connected": False, "reason": str(e)}


def _parse_quotation(q: dict) -> float:
    """Parse Tinkoff Quotation to float"""
    units = int(q.get("units", 0))
    nano = int(q.get("nano", 0))
    return units + nano / 1e9


def _parse_money(m: dict) -> float:
    """Parse Tinkoff MoneyValue to float"""
    units = int(m.get("units", 0))
    nano = int(m.get("nano", 0))
    return units + nano / 1e9


def _map_asset_class(instrument_type: str) -> str:
    return {
        "share": "stock",
        "bond": "bond",
        "etf": "etf",
        "futures": "futures",
        "option": "option",
    }.get(instrument_type, "unknown")


def _serialize_holdings(holdings):
    """Ensure all fields are JSON-serializable"""
    return [{k: v for k, v in h.items()} for h in holdings]
