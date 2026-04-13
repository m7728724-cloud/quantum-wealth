"""Tinkoff Investments Portfolio Sync Service"""
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


def _get_token():
    return os.environ.get("TINKOFF_TOKEN", "")


def sync_portfolio(db) -> Dict[str, Any]:
    """Fetch portfolio from Tinkoff and sync to MongoDB holdings collection.

    Returns dict with sync status and holdings list.
    """
    token = _get_token()
    if not token:
        return {"error": "TINKOFF_TOKEN not configured", "holdings": []}

    try:
        from tinkoff.invest import Client, MoneyValue
        from tinkoff.invest.services import InstrumentsService

        with Client(token) as tink_client:
            # Get all accounts
            accounts = tink_client.users.get_accounts()
            if not accounts.accounts:
                return {"error": "No accounts found in Tinkoff", "holdings": []}

            account_id = accounts.accounts[0].id
            logger.info(f"Tinkoff account: {account_id}")

            # Get portfolio
            portfolio = tink_client.operations.get_portfolio(account_id=account_id)

            synced = []
            for pos in portfolio.positions:
                figi = pos.figi
                quantity = _money_to_float(pos.quantity)
                avg_price = _money_to_float(pos.average_position_price)
                current_price = _money_to_float(pos.current_price)
                instrument_type = pos.instrument_type

                if quantity == 0:
                    continue

                # Resolve instrument details
                try:
                    if instrument_type == "share":
                        info = tink_client.instruments.share_by(id_type=1, id=figi)
                        inst = info.instrument
                        asset_class = "stock"
                    elif instrument_type == "bond":
                        info = tink_client.instruments.bond_by(id_type=1, id=figi)
                        inst = info.instrument
                        asset_class = "bond"
                    elif instrument_type == "etf":
                        info = tink_client.instruments.etf_by(id_type=1, id=figi)
                        inst = info.instrument
                        asset_class = "etf"
                    elif instrument_type == "currency":
                        # Skip cash positions
                        continue
                    else:
                        info = tink_client.instruments.find_instrument(query=figi)
                        inst = None
                        asset_class = "unknown"

                    ticker = getattr(inst, 'ticker', figi) if inst else figi
                    name = getattr(inst, 'name', ticker) if inst else ticker
                    isin_val = getattr(inst, 'isin', '') if inst else ''

                    # Check if it's a liquidity fund
                    is_liq = ticker.upper() in ("LQDT", "SBMM", "VTBM", "TMON", "AMNR")
                    if is_liq:
                        asset_class = "liquidity_fund"

                except Exception as e:
                    logger.warning(f"Could not resolve instrument {figi}: {e}")
                    ticker = figi
                    name = figi
                    isin_val = ""
                    is_liq = False

                holding = {
                    "isin": isin_val or figi,
                    "secid": ticker,
                    "shortname": name,
                    "fullname": name,
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

                # Upsert: update if exists (by figi), insert if new
                db.holdings.update_one(
                    {"figi": figi},
                    {"$set": holding},
                    upsert=True
                )
                synced.append(holding)

            # Get total portfolio value
            total_value = _money_to_float(portfolio.total_amount_portfolio)

            return {
                "status": "success",
                "account_id": account_id,
                "holdings_synced": len(synced),
                "total_portfolio_value": total_value,
                "currency": "RUB",
                "synced_at": datetime.now().isoformat(),
                "holdings": synced
            }

    except ImportError:
        logger.error("tinkoff-investments package not installed")
        return {"error": "tinkoff-investments package not installed. Run: pip install tinkoff-investments", "holdings": []}
    except Exception as e:
        logger.error(f"Tinkoff sync error: {e}")
        return {"error": str(e), "holdings": []}


def get_tinkoff_status() -> Dict[str, Any]:
    """Check if Tinkoff connection is configured and working"""
    token = _get_token()
    if not token:
        return {"connected": False, "reason": "TINKOFF_TOKEN not set"}

    try:
        from tinkoff.invest import Client
        with Client(token) as tink_client:
            accounts = tink_client.users.get_accounts()
            return {
                "connected": True,
                "accounts": len(accounts.accounts),
                "account_id": accounts.accounts[0].id if accounts.accounts else None
            }
    except ImportError:
        return {"connected": False, "reason": "tinkoff-investments not installed"}
    except Exception as e:
        return {"connected": False, "reason": str(e)}


def _money_to_float(money_value) -> float:
    """Convert Tinkoff MoneyValue/Quotation to float"""
    if money_value is None:
        return 0.0
    if hasattr(money_value, 'units') and hasattr(money_value, 'nano'):
        return float(money_value.units) + float(money_value.nano) / 1e9
    return 0.0
