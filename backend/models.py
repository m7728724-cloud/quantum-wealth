"""Pydantic models and MongoDB schema definitions"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AssetClass(str, Enum):
    STOCK = "stock"
    BOND = "bond"
    LIQUIDITY_FUND = "liquidity_fund"
    ETF = "etf"
    UNKNOWN = "unknown"


class TradeDirection(str, Enum):
    CALL = "CALL"
    PUT = "PUT"


class TradeResult(str, Enum):
    WIN = "WIN"
    LOSS = "LOSS"
    DRAW = "DRAW"
    PENDING = "PENDING"


class RuleSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# --- Portfolio ---
class HoldingCreate(BaseModel):
    isin: str
    quantity: float = 1.0
    buy_price: Optional[float] = None
    notes: Optional[str] = None


class HoldingResponse(BaseModel):
    id: str
    isin: str
    secid: str
    shortname: str
    fullname: str
    asset_class: str
    group: Optional[str] = None
    quantity: float
    buy_price: Optional[float] = None
    notes: Optional[str] = None
    is_liquidity_fund: bool = False
    created_at: str
    updated_at: str


# --- Trades (BO Journal) ---
class TradeCreate(BaseModel):
    asset: str
    direction: TradeDirection
    expiry_seconds: Optional[int] = 60
    amount: Optional[float] = None
    result: TradeResult = TradeResult.PENDING
    notes: Optional[str] = None
    signal_id: Optional[str] = None


class TradeUpdate(BaseModel):
    result: TradeResult
    notes: Optional[str] = None


# --- Signals (TradingView Webhooks) ---
class WebhookSignal(BaseModel):
    symbol: Optional[str] = None
    action: Optional[str] = None
    timeframe: Optional[str] = None
    price: Optional[float] = None
    indicator: Optional[str] = None
    message: Optional[str] = None


# --- AI Insights ---
class AIInsightRequest(BaseModel):
    focus: Optional[str] = "full_portfolio"
    custom_prompt: Optional[str] = None


# --- Memory ---
class MemoryLogCreate(BaseModel):
    interaction_type: str  # recommendation, analysis, trade_review
    content: str
    outcome: Optional[str] = None
    tags: List[str] = []


# --- Safeguard Rules ---
class SafeguardRuleCreate(BaseModel):
    rule_text: str
    severity: RuleSeverity = RuleSeverity.MEDIUM
    confidence: float = 0.5
    source: str = "manual"
    related_assets: List[str] = []


# --- Auth ---
class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    created_at: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
