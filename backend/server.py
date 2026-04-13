"""
Quantum Wealth & BO Platform - Main FastAPI Server
Military-grade secure, self-learning trading terminal
"""
import os
import logging
import asyncio
import threading
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Optional, List

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient, DESCENDING
from bson import ObjectId

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from models import (
    HoldingCreate, TradeCreate, TradeUpdate, WebhookSignal,
    AIInsightRequest, MemoryLogCreate, SafeguardRuleCreate,
    UserLogin, TokenResponse
)
from services.moex_service import resolve_isin, get_security_market_data
from services.ai_service import analyze_portfolio, generate_safeguard_rules, ai_filter_signal
from services.news_service import fetch_all_feeds
from services.memory_service import (
    retrieve_relevant_memories, retrieve_safeguard_rules,
    log_memory, save_safeguard_rules
)
from services.signal_brain import scan_all_pairs, analyze_pair, calculate_indicator_performance
from services.price_data import fetch_candles, fetch_multi, get_supported_symbols, get_current_price
from services.tinkoff_service import sync_portfolio, get_tinkoff_status
from utils.auth import (
    hash_password, verify_password, create_token,
    get_current_user, require_auth
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# MongoDB
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "quantum_wealth")

import certifi
client = MongoClient(MONGO_URL, tlsCAFile=certifi.where())
db = client[DB_NAME]


def serialize_doc(doc):
    """Serialize MongoDB document for JSON response"""
    if doc is None:
        return None
    if isinstance(doc, list):
        return [serialize_doc(d) for d in doc]
    if isinstance(doc, dict):
        result = {}
        for key, value in doc.items():
            if key == "_id":
                result["id"] = str(value)
            elif isinstance(value, ObjectId):
                result[key] = str(value)
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, dict):
                result[key] = serialize_doc(value)
            elif isinstance(value, list):
                result[key] = [serialize_doc(v) if isinstance(v, dict) else v for v in value]
            else:
                result[key] = value
        return result
    return doc


def seed_admin():
    """Seed the admin account on startup"""
    existing = db.users.find_one({"username": "Vika-net1"})
    if not existing:
        admin = {
            "username": "Vika-net1",
            "password_hash": hash_password("Dd19840622"),
            "role": "admin",
            "created_at": datetime.now().isoformat(),
        }
        db.users.insert_one(admin)
        logger.info("Admin account seeded: Vika-net1")
    else:
        logger.info("Admin account already exists")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting Quantum Wealth & BO Platform...")
    seed_admin()
    # Create indexes
    db.holdings.create_index("isin")
    db.holdings.create_index("user")
    db.trades.create_index([("created_at", DESCENDING)])
    db.signals.create_index([("received_at", DESCENDING)])
    db.memory.create_index([("created_at", DESCENDING)])
    db.news_cache.create_index([("fetched_at", DESCENDING)])
    db.safeguard_rules.create_index("active")
    logger.info("Database indexes created")
    yield
    client.close()


app = FastAPI(
    title="Quantum Wealth & BO Platform",
    version="1.0.0",
    lifespan=lifespan
)

# Rate limiting
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# Health Check
# ============================================
@app.get("/api/health")
async def health_check():
    return {
        "status": "operational",
        "platform": "Quantum Wealth & BO Platform",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


# ============================================
# Authentication
# ============================================
@app.post("/api/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, data: UserLogin):
    """Login with username/password - rate limited"""
    user = db.users.find_one({"username": data.username})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(data.username)
    return TokenResponse(
        access_token=token,
        username=data.username
    )


@app.get("/api/auth/me")
async def get_me(request: Request):
    """Get current authenticated user"""
    username = require_auth(request)
    user = db.users.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "role": user.get("role", "user"),
        "created_at": user.get("created_at", "")
    }


# ============================================
# Portfolio (ISIN Resolution + Holdings)
# ============================================
@app.post("/api/portfolio/resolve-isin")
async def resolve_isin_endpoint(request: Request, data: dict = Body(...)):
    """Resolve an ISIN code to human-readable name via MOEX API"""
    require_auth(request)
    isin = data.get("isin", "").strip().upper()
    if not isin:
        raise HTTPException(status_code=400, detail="ISIN code required")
    
    result = resolve_isin(isin)
    if not result:
        raise HTTPException(status_code=404, detail=f"Could not resolve ISIN: {isin}")
    
    return result


@app.post("/api/portfolio/holdings")
async def add_holding(request: Request, data: HoldingCreate):
    """Add a portfolio holding - auto-resolves ISIN via MOEX"""
    require_auth(request)
    isin = data.isin.strip().upper()
    
    # Resolve ISIN
    resolved = resolve_isin(isin)
    if not resolved:
        raise HTTPException(status_code=404, detail=f"Could not resolve ISIN: {isin}. Please check the code.")
    
    # Check for duplicate
    existing = db.holdings.find_one({"isin": isin})
    if existing:
        # Update quantity
        db.holdings.update_one(
            {"_id": existing["_id"]},
            {"$inc": {"quantity": data.quantity},
             "$set": {"updated_at": datetime.now().isoformat()}}
        )
        updated = db.holdings.find_one({"_id": existing["_id"]})
        return serialize_doc(updated)
    
    holding = {
        "isin": isin,
        "secid": resolved["secid"],
        "shortname": resolved["shortname"],
        "fullname": resolved["fullname"],
        "asset_class": resolved["asset_class"],
        "group": resolved.get("group", ""),
        "is_liquidity_fund": resolved.get("is_liquidity_fund", False),
        "quantity": data.quantity,
        "buy_price": data.buy_price,
        "notes": data.notes,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    
    result = db.holdings.insert_one(holding)
    holding["_id"] = result.inserted_id
    return serialize_doc(holding)


@app.get("/api/portfolio/holdings")
async def get_holdings(request: Request):
    """Get all portfolio holdings with resolved names"""
    require_auth(request)
    holdings = list(db.holdings.find().sort("created_at", DESCENDING))
    return serialize_doc(holdings)


@app.delete("/api/portfolio/holdings/{holding_id}")
async def delete_holding(holding_id: str, request: Request):
    """Delete a holding"""
    require_auth(request)
    try:
        result = db.holdings.delete_one({"_id": ObjectId(holding_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Holding not found")
        return {"status": "deleted", "id": holding_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================
# News Feed
# ============================================
@app.post("/api/news/refresh")
async def refresh_news(request: Request):
    """Fetch latest news from RSS feeds and cache"""
    require_auth(request)
    articles = fetch_all_feeds(max_per_feed=10)
    
    # Cache in MongoDB
    if articles:
        # Clear old cache
        db.news_cache.delete_many({})
        for art in articles:
            db.news_cache.insert_one(art)
    
    # Re-read from DB to get proper serialization
    cached = list(db.news_cache.find().sort("fetched_at", -1))
    return {"status": "refreshed", "count": len(cached), "articles": serialize_doc(cached)}


@app.get("/api/news")
async def get_news(request: Request, region: Optional[str] = None, limit: int = 30):
    """Get cached news articles"""
    require_auth(request)
    query = {}
    if region:
        query["region"] = region
    
    articles = list(
        db.news_cache.find(query)
        .sort("fetched_at", DESCENDING)
        .limit(limit)
    )
    
    if not articles:
        # Auto-refresh if cache empty
        fresh = fetch_all_feeds(max_per_feed=10)
        if fresh:
            for art in fresh:
                db.news_cache.insert_one(art)
            articles = fresh[:limit]
    
    return serialize_doc(articles)


# ============================================
# AI Insights
# ============================================
@app.post("/api/ai/portfolio-insight")
async def get_portfolio_insight(request: Request, data: AIInsightRequest = None):
    """Generate AI-powered portfolio analysis"""
    require_auth(request)
    if data is None:
        data = AIInsightRequest()
    
    # Get holdings
    holdings = list(db.holdings.find())
    if not holdings:
        return {"error": "No holdings in portfolio. Add holdings first."}
    
    holdings_data = serialize_doc(holdings)
    
    # Get news
    news = list(db.news_cache.find().sort("fetched_at", DESCENDING).limit(15))
    news_data = serialize_doc(news)
    
    # Get memory
    memories = list(db.memory.find().sort("created_at", DESCENDING).limit(10))
    memory_data = serialize_doc(memories)
    
    # Get safeguard rules
    safeguards = list(db.safeguard_rules.find({"active": True}))
    safeguard_data = serialize_doc(safeguards)
    
    # Generate analysis
    result = await analyze_portfolio(
        holdings=holdings_data,
        news_items=news_data,
        memory_items=memory_data,
        safeguard_rules=safeguard_data,
        custom_prompt=data.custom_prompt
    )
    
    # Log this interaction in memory
    if "error" not in result:
        log_memory(
            db,
            interaction_type="portfolio_analysis",
            content=result.get("portfolio_summary", "Analysis generated"),
            outcome=result.get("risk_assessment", "unknown"),
            tags=["ai_analysis", "portfolio"]
        )
    
    return result


# ============================================
# TradingView Signals (Webhook Listener)
# ============================================
@app.post("/api/signals/webhook")
async def receive_webhook(request: Request, data: WebhookSignal = None):
    """Receive TradingView webhook signals"""
    # Accept both structured and raw payload
    if data is None:
        try:
            body = await request.json()
        except Exception:
            body = {"message": (await request.body()).decode("utf-8", errors="replace")}
    else:
        body = data.dict()
    
    signal = {
        "symbol": body.get("symbol", body.get("ticker", "UNKNOWN")),
        "action": body.get("action", body.get("strategy", {}).get("order_action", "UNKNOWN")).upper() if isinstance(body.get("action", body.get("strategy", {}).get("order_action", "UNKNOWN")), str) else "UNKNOWN",
        "timeframe": body.get("timeframe", body.get("interval", "")),
        "price": body.get("price", body.get("close", None)),
        "indicator": body.get("indicator", body.get("strategy_name", "")),
        "message": body.get("message", ""),
        "raw_payload": body,
        "received_at": datetime.now().isoformat(),
        "logged_as_trade": False
    }
    
    result = db.signals.insert_one(signal)
    signal["_id"] = result.inserted_id
    
    logger.info(f"Webhook signal received: {signal['symbol']} {signal['action']}")
    return serialize_doc(signal)


@app.get("/api/signals")
async def get_signals(request: Request, limit: int = 50):
    """Get received TradingView signals"""
    require_auth(request)
    signals = list(
        db.signals.find()
        .sort("received_at", DESCENDING)
        .limit(limit)
    )
    return serialize_doc(signals)


@app.delete("/api/signals/{signal_id}")
async def delete_signal(signal_id: str, request: Request):
    """Delete a signal"""
    require_auth(request)
    try:
        result = db.signals.delete_one({"_id": ObjectId(signal_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Signal not found")
        return {"status": "deleted", "id": signal_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================
# Binary Options Trade Journal
# ============================================
@app.post("/api/trades")
async def create_trade(request: Request, data: TradeCreate):
    """Log a binary options trade"""
    require_auth(request)
    trade = {
        "asset": data.asset,
        "direction": data.direction.value,
        "expiry_seconds": data.expiry_seconds,
        "amount": data.amount,
        "result": data.result.value,
        "notes": data.notes,
        "signal_id": data.signal_id,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    
    result = db.trades.insert_one(trade)
    trade["_id"] = result.inserted_id
    
    # If from signal, mark it as logged
    if data.signal_id:
        try:
            db.signals.update_one(
                {"_id": ObjectId(data.signal_id)},
                {"$set": {"logged_as_trade": True}}
            )
        except Exception:
            pass
    
    return serialize_doc(trade)


@app.get("/api/trades")
async def get_trades(request: Request, result_filter: Optional[str] = None, limit: int = 100):
    """Get trade journal entries"""
    require_auth(request)
    query = {}
    if result_filter:
        query["result"] = result_filter.upper()
    
    trades = list(
        db.trades.find(query)
        .sort("created_at", DESCENDING)
        .limit(limit)
    )
    return serialize_doc(trades)


@app.put("/api/trades/{trade_id}")
async def update_trade(trade_id: str, request: Request, data: TradeUpdate):
    """Update trade result (Win/Loss/Draw)"""
    require_auth(request)
    try:
        update = {
            "result": data.result.value,
            "updated_at": datetime.now().isoformat()
        }
        if data.notes is not None:
            update["notes"] = data.notes
        
        result = db.trades.update_one(
            {"_id": ObjectId(trade_id)},
            {"$set": update}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Trade not found")
        
        updated = db.trades.find_one({"_id": ObjectId(trade_id)})
        return serialize_doc(updated)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/trades/stats")
async def get_trade_stats(request: Request):
    """Get trading statistics with detailed analytics"""
    require_auth(request)
    total = db.trades.count_documents({})
    wins = db.trades.count_documents({"result": "WIN"})
    losses = db.trades.count_documents({"result": "LOSS"})
    draws = db.trades.count_documents({"result": "DRAW"})
    pending = db.trades.count_documents({"result": "PENDING"})
    
    win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
    
    # Asset breakdown
    asset_pipeline = [
        {"$match": {"result": {"$in": ["WIN", "LOSS"]}}},
        {"$group": {
            "_id": "$asset",
            "wins": {"$sum": {"$cond": [{"$eq": ["$result", "WIN"]}, 1, 0]}},
            "losses": {"$sum": {"$cond": [{"$eq": ["$result", "LOSS"]}, 1, 0]}},
            "total": {"$sum": 1}
        }}
    ]
    asset_stats = list(db.trades.aggregate(asset_pipeline))
    
    # Direction breakdown
    direction_pipeline = [
        {"$match": {"result": {"$in": ["WIN", "LOSS"]}}},
        {"$group": {
            "_id": "$direction",
            "wins": {"$sum": {"$cond": [{"$eq": ["$result", "WIN"]}, 1, 0]}},
            "losses": {"$sum": {"$cond": [{"$eq": ["$result", "LOSS"]}, 1, 0]}},
            "total": {"$sum": 1}
        }}
    ]
    direction_stats = list(db.trades.aggregate(direction_pipeline))
    
    # Expiry breakdown
    expiry_pipeline = [
        {"$match": {"result": {"$in": ["WIN", "LOSS"]}}},
        {"$group": {
            "_id": "$expiry_seconds",
            "wins": {"$sum": {"$cond": [{"$eq": ["$result", "WIN"]}, 1, 0]}},
            "losses": {"$sum": {"$cond": [{"$eq": ["$result", "LOSS"]}, 1, 0]}},
            "total": {"$sum": 1}
        }}
    ]
    expiry_stats = list(db.trades.aggregate(expiry_pipeline))
    
    # Recent trade results for chart (last 20)
    recent_trades = list(
        db.trades.find(
            {"result": {"$in": ["WIN", "LOSS"]}},
            {"result": 1, "asset": 1, "created_at": 1, "direction": 1}
        ).sort("created_at", DESCENDING).limit(20)
    )
    recent_chart = []
    for i, t in enumerate(reversed(recent_trades)):
        recent_chart.append({
            "index": i + 1,
            "result": 1 if t["result"] == "WIN" else 0,
            "asset": t.get("asset", ""),
            "direction": t.get("direction", "")
        })
    
    return {
        "total": total,
        "wins": wins,
        "losses": losses,
        "draws": draws,
        "pending": pending,
        "win_rate": round(win_rate, 1),
        "asset_breakdown": asset_stats,
        "direction_breakdown": direction_stats,
        "expiry_breakdown": expiry_stats,
        "recent_chart": recent_chart
    }


@app.get("/api/portfolio/allocation")
async def get_portfolio_allocation(request: Request):
    """Get portfolio allocation breakdown by asset class"""
    require_auth(request)
    pipeline = [
        {"$group": {
            "_id": "$asset_class",
            "count": {"$sum": 1},
            "total_quantity": {"$sum": "$quantity"},
            "assets": {"$push": {"name": "$shortname", "qty": "$quantity", "secid": "$secid"}}
        }}
    ]
    allocation = list(db.holdings.aggregate(pipeline))
    return allocation


# ============================================
# Adaptive Memory & Safeguard Rules
# ============================================
@app.get("/api/memory")
async def get_memory_entries(request: Request, limit: int = 50):
    """Get memory log entries"""
    require_auth(request)
    memories = list(
        db.memory.find()
        .sort("created_at", DESCENDING)
        .limit(limit)
    )
    return serialize_doc(memories)


@app.post("/api/memory")
async def create_memory_entry(request: Request, data: MemoryLogCreate):
    """Log a memory entry"""
    require_auth(request)
    entry = log_memory(
        db,
        interaction_type=data.interaction_type,
        content=data.content,
        outcome=data.outcome,
        tags=data.tags
    )
    return serialize_doc(entry)


@app.get("/api/safeguards")
async def get_safeguard_rules(request: Request):
    """Get all safeguard rules"""
    require_auth(request)
    rules = list(
        db.safeguard_rules.find()
        .sort("created_at", DESCENDING)
    )
    return serialize_doc(rules)


@app.post("/api/safeguards/generate")
async def generate_safeguards(request: Request):
    """AI-analyze losses and generate new safeguard rules"""
    require_auth(request)
    # Get loss trades
    loss_trades = list(db.trades.find({"result": "LOSS"}).sort("created_at", DESCENDING).limit(50))
    
    if not loss_trades:
        return {"message": "No loss trades found. Log some trades with LOSS result first.", "rules": []}
    
    loss_data = serialize_doc(loss_trades)
    existing_rules = list(db.safeguard_rules.find({"active": True}))
    existing_data = serialize_doc(existing_rules)
    
    # Generate rules via AI
    new_rules = await generate_safeguard_rules(loss_data, existing_data)
    
    # Save to DB
    saved = save_safeguard_rules(db, new_rules)
    
    # Log in memory
    log_memory(
        db,
        interaction_type="safeguard_generation",
        content=f"Generated {len(saved)} new safeguard rules from {len(loss_trades)} loss trades",
        tags=["safeguard", "ai_generated"]
    )
    
    return {"rules": serialize_doc(saved), "analyzed_losses": len(loss_trades)}


@app.put("/api/safeguards/{rule_id}/toggle")
async def toggle_safeguard(rule_id: str, request: Request):
    """Toggle a safeguard rule active/inactive"""
    require_auth(request)
    try:
        rule = db.safeguard_rules.find_one({"_id": ObjectId(rule_id)})
        if not rule:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        new_status = not rule.get("active", True)
        db.safeguard_rules.update_one(
            {"_id": ObjectId(rule_id)},
            {"$set": {"active": new_status}}
        )
        
        updated = db.safeguard_rules.find_one({"_id": ObjectId(rule_id)})
        return serialize_doc(updated)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/safeguards/{rule_id}")
async def delete_safeguard(rule_id: str, request: Request):
    """Delete a safeguard rule"""
    require_auth(request)
    try:
        result = db.safeguard_rules.delete_one({"_id": ObjectId(rule_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Rule not found")
        return {"status": "deleted", "id": rule_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/safeguards/manual")
async def add_manual_safeguard(request: Request, data: SafeguardRuleCreate):
    """Add a manual safeguard rule"""
    require_auth(request)
    doc = {
        "rule_text": data.rule_text,
        "severity": data.severity.value,
        "confidence": data.confidence,
        "pattern_found": "",
        "related_assets": data.related_assets,
        "source": "manual",
        "active": True,
        "created_at": datetime.now().isoformat(),
    }
    result = db.safeguard_rules.insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize_doc(doc)


# ============================================
# Dashboard Stats
# ============================================
@app.get("/api/dashboard/stats")
async def get_dashboard_stats(request: Request):
    """Get dashboard summary stats"""
    require_auth(request)
    holdings_count = db.holdings.count_documents({})
    trades_count = db.trades.count_documents({})
    signals_count = db.signals.count_documents({})
    rules_count = db.safeguard_rules.count_documents({"active": True})
    news_count = db.news_cache.count_documents({})
    
    wins = db.trades.count_documents({"result": "WIN"})
    losses = db.trades.count_documents({"result": "LOSS"})
    win_rate = round((wins / (wins + losses) * 100), 1) if (wins + losses) > 0 else 0
    
    return {
        "holdings": holdings_count,
        "trades": trades_count,
        "signals": signals_count,
        "active_rules": rules_count,
        "news_articles": news_count,
        "win_rate": win_rate,
        "wins": wins,
        "losses": losses,
        "timestamp": datetime.now().isoformat()
    }


# ============================================
# Quantum Signal Brain — BO Signal Scanner
# ============================================
_auto_scan_task = None
_auto_scan_running = False
DEFAULT_PAIRS = ["EURUSD", "USDJPY", "AUDUSD", "AUDJPY", "EURJPY", "USDCAD"]
DEFAULT_EXPIRIES = [300, 600, 900]  # 5min, 10min, 15min in seconds


@app.get("/api/signals/scan")
async def scan_signals(request: Request):
    """Manually trigger a scan of all configured pairs"""
    require_auth(request)
    try:
        # Fetch price data for all pairs
        price_data = fetch_multi(DEFAULT_PAIRS, interval="1m")
        if not price_data:
            return {"signals": [], "message": "Could not fetch price data. Market may be closed."}

        # Run confluence analysis
        raw_signals = scan_all_pairs(price_data)

        # Get context for AI filter
        news_items = list(db.news_cache.find().sort("fetched_at", DESCENDING).limit(10))
        safeguard_rules_list = list(db.safeguard_rules.find({"active": True}))

        approved_signals = []
        for sig in raw_signals:
            symbol = sig["symbol"]

            # Get recent trades for this asset
            recent_trades = list(
                db.trades.find({"asset": symbol}).sort("created_at", DESCENDING).limit(10)
            )

            # AI filter
            ai_verdict = await ai_filter_signal(
                sig,
                news_items=[serialize_doc(n) for n in news_items],
                safeguard_rules=[serialize_doc(s) for s in safeguard_rules_list],
                recent_trades=[serialize_doc(t) for t in recent_trades]
            )

            sig["ai_filter"] = ai_verdict
            sig["approved"] = ai_verdict.get("approved", True)
            sig["expiry_options"] = DEFAULT_EXPIRIES

            # Save to signals collection
            signal_doc = {
                **sig,
                "source": "quantum_brain",
                "received_at": datetime.now().isoformat(),
                "logged_as_trade": False
            }
            result = db.signals.insert_one(signal_doc)
            sig["id"] = str(result.inserted_id)

            approved_signals.append(sig)

            # Log in memory
            log_memory(
                db,
                interaction_type="signal_generated",
                content=f"{sig['direction']} {symbol} | Confluence: {sig['confluence_score']}/6 | Confidence: {sig['confidence']}% | AI: {'OK' if sig['approved'] else 'BLOCKED'}",
                tags=["signal", symbol, sig["direction"]]
            )

        return {
            "signals": approved_signals,
            "total_scanned": len(price_data),
            "total_generated": len(raw_signals),
            "total_approved": len([s for s in approved_signals if s["approved"]]),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Signal scan error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/signals/performance")
async def get_signal_performance(request: Request):
    """Get signal accuracy stats by indicator and pair"""
    require_auth(request)
    trades = list(db.trades.find({"result": {"$in": ["WIN", "LOSS"]}}).limit(500))
    perf = calculate_indicator_performance(trades)

    # Per-pair stats
    pair_stats = {}
    for trade in trades:
        asset = trade.get("asset", "UNKNOWN")
        if asset not in pair_stats:
            pair_stats[asset] = {"wins": 0, "losses": 0, "total": 0}
        pair_stats[asset]["total"] += 1
        if trade.get("result") == "WIN":
            pair_stats[asset]["wins"] += 1
        else:
            pair_stats[asset]["losses"] += 1

    for asset, data in pair_stats.items():
        data["win_rate"] = round(data["wins"] / data["total"] * 100, 1) if data["total"] > 0 else 0

    return {
        "indicator_performance": perf,
        "pair_performance": pair_stats,
        "total_trades_analyzed": len(trades)
    }


@app.get("/api/signals/supported-pairs")
async def get_supported_pairs(request: Request):
    """Get list of supported forex pairs"""
    require_auth(request)
    return {
        "pairs": DEFAULT_PAIRS,
        "all_available": get_supported_symbols(),
        "expiry_options": DEFAULT_EXPIRIES
    }


# ============================================
# Tinkoff Portfolio Sync
# ============================================
@app.post("/api/tinkoff/sync")
async def tinkoff_sync(request: Request):
    """Sync portfolio from Tinkoff Investments"""
    require_auth(request)
    try:
        result = sync_portfolio(db)
        if "error" not in result:
            log_memory(
                db,
                interaction_type="tinkoff_sync",
                content=f"Synced {result.get('holdings_synced', 0)} positions from Tinkoff. Total value: {result.get('total_portfolio_value', 0)} RUB",
                tags=["tinkoff", "portfolio_sync"]
            )
        return result
    except Exception as e:
        logger.error(f"Tinkoff sync error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tinkoff/status")
async def tinkoff_connection_status(request: Request):
    """Check Tinkoff connection status"""
    require_auth(request)
    return get_tinkoff_status()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
