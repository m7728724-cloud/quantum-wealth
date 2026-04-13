"""Claude AI Service via OpenRouter — Portfolio Analysis & Safeguard Generation"""
import os
import json
import logging
import httpx
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "anthropic/claude-sonnet-4-20250514"


def _get_api_key():
    return os.environ.get("OPENROUTER_API_KEY", "")


async def _call_claude(system_message: str, user_message: str) -> str:
    """Send a request to Claude via OpenRouter API"""
    api_key = _get_api_key()
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not configured")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://quantum-wealth.app",
        "X-Title": "Quantum Wealth AI Terminal"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.3,
        "max_tokens": 4096
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(OPENROUTER_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


def _clean_json_response(raw: str) -> str:
    """Strip markdown code fences from AI response"""
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
    return cleaned


async def analyze_portfolio(
    holdings: List[Dict],
    news_items: List[Dict],
    memory_items: List[Dict] = None,
    safeguard_rules: List[Dict] = None,
    custom_prompt: str = None
) -> Dict[str, Any]:
    """Generate AI portfolio analysis using Claude via OpenRouter"""
    try:
        api_key = _get_api_key()
        if not api_key:
            return {"error": "AI service not configured (missing OPENROUTER_API_KEY)"}

        system_message = """You are the Quantum Wealth AI - an institutional-grade quantitative analyst for MOEX (Moscow Exchange) portfolio assets.

CRITICAL RULES:
1. For Liquidity Funds (LQDT, SBMM, VTBM, or any asset marked is_liquidity_fund=true): IGNORE ALL technical indicators (RSI, MACD, Bollinger Bands, etc.). Treat them PURELY as interest-bearing cash equivalents yielding at the current Central Bank rate.
2. You MUST read and incorporate any Adaptive Memory safeguard rules provided.
3. Cross-reference holdings against the provided news for macro-cognitive analysis.
4. Consider geopolitical risks, central bank rate cycles, and crowd behavior sentiment.
5. Respond in Russian language for text fields.

Always respond in valid JSON with this exact schema:
{
  "portfolio_summary": "string - overall portfolio health assessment",
  "risk_assessment": "low|medium|high|critical",
  "macro_view": "string - geopolitical and macro analysis",
  "insights": ["array of specific insight strings"],
  "action_items": ["array of recommended actions"],
  "liquidity_fund_note": "string - only if liquidity funds present, explain yield/cash treatment",
  "safeguards_applied": ["array of relevant safeguard rules that were considered"],
  "confidence": 0.0-1.0
}"""

        # Build context
        portfolio_text = json.dumps(holdings, indent=2, ensure_ascii=False)

        news_text = "No recent news available."
        if news_items:
            news_lines = []
            for n in news_items[:15]:
                news_lines.append(f"[{n.get('source', 'Unknown')}] {n.get('title', '')}")
            news_text = "\n".join(news_lines)

        memory_text = "No memory/history available."
        if memory_items:
            mem_lines = []
            for m in memory_items[:10]:
                mem_lines.append(f"- [{m.get('interaction_type', '')}] {m.get('content', '')[:150]}")
            memory_text = "\n".join(mem_lines)

        safeguard_text = "No safeguard rules active."
        if safeguard_rules:
            sg_lines = []
            for s in safeguard_rules:
                sg_lines.append(f"- [{s.get('severity', 'medium')}] {s.get('rule_text', '')}")
            safeguard_text = "\n".join(sg_lines)

        prompt = f"""FULL PORTFOLIO ANALYSIS REQUEST

PORTFOLIO HOLDINGS:
{portfolio_text}

LATEST NEWS HEADLINES:
{news_text}

ADAPTIVE MEMORY (Past Interactions):
{memory_text}

ACTIVE SAFEGUARD RULES:
{safeguard_text}"""

        if custom_prompt:
            prompt += f"\n\nADDITIONAL USER FOCUS:\n{custom_prompt}"

        prompt += "\n\nRespond ONLY in valid JSON matching the schema. No markdown wrapping."

        response = await _call_claude(system_message, prompt)
        cleaned = _clean_json_response(response)

        try:
            result = json.loads(cleaned)
            result["generated_at"] = datetime.now().isoformat()
            return result
        except json.JSONDecodeError:
            return {
                "portfolio_summary": cleaned[:500],
                "risk_assessment": "unknown",
                "insights": ["AI response could not be parsed as structured JSON"],
                "action_items": [],
                "confidence": 0.3,
                "raw_response": cleaned,
                "generated_at": datetime.now().isoformat()
            }

    except Exception as e:
        logger.error(f"AI analysis error: {e}")
        return {"error": str(e), "generated_at": datetime.now().isoformat()}


async def generate_safeguard_rules(
    loss_trades: List[Dict],
    existing_rules: List[Dict] = None
) -> List[Dict]:
    """Analyze losses and generate new safeguard rules via Claude"""
    try:
        api_key = _get_api_key()
        if not api_key:
            return [{"error": "AI service not configured"}]

        if not loss_trades:
            return []

        system_message = """You are a trading risk analyst. Analyze binary options trade losses to find hidden patterns and correlations.

Generate safeguard rules that prevent the trader from repeating mistakes.
Look for:
- Time-of-day patterns (e.g., losses cluster during specific hours)
- Asset-specific patterns (e.g., certain pairs lose more)
- News correlation (e.g., losses during macro news releases)
- Direction bias (e.g., too many CALLs on trending-down assets)
- Expiry patterns (e.g., 60s expiry loses more than 300s)

Respond in Russian language for rule_text field.
Respond ONLY in valid JSON array:
[
  {
    "rule_text": "string - clear, actionable rule",
    "severity": "low|medium|high",
    "confidence": 0.0-1.0,
    "pattern_found": "string - what pattern was detected",
    "related_assets": ["asset strings"]
  }
]"""

        trades_text = json.dumps(loss_trades, indent=2, ensure_ascii=False)

        existing_text = "None"
        if existing_rules:
            existing_text = json.dumps([r.get("rule_text", "") for r in existing_rules])

        prompt = f"""LOSS TRADE ANALYSIS

LOSS TRADES ({len(loss_trades)} total):
{trades_text}

EXISTING RULES (do not duplicate):
{existing_text}

Analyze these losses. Find hidden correlations and generate NEW safeguard rules.
Respond ONLY in valid JSON array."""

        response = await _call_claude(system_message, prompt)
        cleaned = _clean_json_response(response)

        try:
            rules = json.loads(cleaned)
            if isinstance(rules, list):
                return rules
            return [rules]
        except json.JSONDecodeError:
            return [{"rule_text": cleaned[:300], "severity": "medium", "confidence": 0.3, "error": "parse_failed"}]

    except Exception as e:
        logger.error(f"Safeguard generation error: {e}")
        return [{"error": str(e)}]


async def ai_filter_signal(
    signal_data: Dict,
    news_items: List[Dict] = None,
    safeguard_rules: List[Dict] = None,
    recent_trades: List[Dict] = None
) -> Dict[str, Any]:
    """AI filter to validate a trading signal before emission"""
    try:
        api_key = _get_api_key()
        if not api_key:
            return {"approved": True, "reason": "AI filter offline — signal passed through"}

        system_message = """You are a trading signal validator. Evaluate if a binary options signal should be taken or blocked.

Consider:
1. Current news that might invalidate the signal
2. Active safeguard rules that might block this trade
3. Recent trade history for this asset (avoid revenge trading)
4. Time of day and market session relevance

Respond in valid JSON:
{
  "approved": true/false,
  "confidence": 0.0-1.0,
  "reason": "string explaining decision in Russian",
  "risk_factors": ["array of risk factor strings"]
}"""

        news_text = "No news available."
        if news_items:
            news_text = "\n".join([f"- {n.get('title', '')}" for n in news_items[:10]])

        safeguard_text = "No active rules."
        if safeguard_rules:
            safeguard_text = "\n".join([f"- [{s.get('severity', 'medium')}] {s.get('rule_text', '')}" for s in safeguard_rules])

        trades_text = "No recent trades."
        if recent_trades:
            trades_text = json.dumps(recent_trades[:10], indent=2, ensure_ascii=False)

        prompt = f"""SIGNAL VALIDATION REQUEST

SIGNAL:
Symbol: {signal_data.get('symbol', 'UNKNOWN')}
Direction: {signal_data.get('direction', 'UNKNOWN')}
Confluence Score: {signal_data.get('confluence_score', 0)}/6
Indicators: {json.dumps(signal_data.get('indicators_triggered', []))}
Confidence: {signal_data.get('confidence', 0)}%

CURRENT NEWS:
{news_text}

ACTIVE SAFEGUARD RULES:
{safeguard_text}

RECENT TRADES FOR THIS ASSET:
{trades_text}

Should this signal be taken? Respond in JSON."""

        response = await _call_claude(system_message, prompt)
        cleaned = _clean_json_response(response)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {"approved": True, "reason": "AI response parse failed — signal passed through", "confidence": 0.5}

    except Exception as e:
        logger.error(f"AI filter error: {e}")
        return {"approved": True, "reason": f"AI filter error: {e} — signal passed through", "confidence": 0.5}
