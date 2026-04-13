"""Claude AI Service - Portfolio Analysis & Safeguard Generation"""
import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
class UserMessage:
    def __init__(self, text):
        self.text = text

class LlmChat:
    def __init__(self, api_key, session_id, system_message):
        self.api_key = api_key
    def with_model(self, provider, model):
        pass
    async def send_message(self, msg):
        if 'LOSS TRADE ANALYSIS' in msg.text:
             return '[{"rule_text": "Mock rule: Avoid trading during API downtime", "severity": "medium", "confidence": 0.9, "pattern_found": "system offline", "related_assets": ["All"]}]'
        return '{"portfolio_summary": "Mock analysis. Configure real API provider in ai_service.py", "risk_assessment": "low", "macro_view": "Neutral", "insights": ["AI offline"], "action_items": [], "confidence": 0.5}'

logger = logging.getLogger(__name__)


def _get_api_key():
    return os.environ.get("EMERGENT_LLM_KEY", "")


async def analyze_portfolio(
    holdings: List[Dict],
    news_items: List[Dict],
    memory_items: List[Dict] = None,
    safeguard_rules: List[Dict] = None,
    custom_prompt: str = None
) -> Dict[str, Any]:
    """Generate AI portfolio analysis using Claude"""
    try:
        api_key = _get_api_key()
        if not api_key:
            return {"error": "AI service not configured (missing API key)"}
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"portfolio-analysis-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            system_message="""You are the Quantum Wealth AI - an institutional-grade quantitative analyst for MOEX (Moscow Exchange) portfolio assets.

CRITICAL RULES:
1. For Liquidity Funds (LQDT, SBMM, VTBM, or any asset marked is_liquidity_fund=true): IGNORE ALL technical indicators (RSI, MACD, Bollinger Bands, etc.). Treat them PURELY as interest-bearing cash equivalents yielding at the current Central Bank rate.
2. You MUST read and incorporate any Adaptive Memory safeguard rules provided.
3. Cross-reference holdings against the provided news for macro-cognitive analysis.
4. Consider geopolitical risks, central bank rate cycles, and crowd behavior sentiment.

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
        )
        chat.with_model("anthropic", "claude-sonnet-4-5-20250929")
        
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
        
        response = await chat.send_message(UserMessage(text=prompt))
        
        # Parse response
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
        
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
    """Analyze losses and generate new safeguard rules"""
    try:
        api_key = _get_api_key()
        if not api_key:
            return [{"error": "AI service not configured"}]
        
        if not loss_trades:
            return []
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"safeguard-gen-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            system_message="""You are a trading risk analyst. Analyze binary options trade losses to find hidden patterns and correlations.

Generate safeguard rules that prevent the trader from repeating mistakes.
Look for:
- Time-of-day patterns (e.g., losses cluster during specific hours)
- Asset-specific patterns (e.g., certain pairs lose more)
- News correlation (e.g., losses during macro news releases)
- Direction bias (e.g., too many CALLs on trending-down assets)
- Expiry patterns (e.g., 60s expiry loses more than 300s)

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
        )
        chat.with_model("anthropic", "claude-sonnet-4-5-20250929")
        
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
        
        response = await chat.send_message(UserMessage(text=prompt))
        
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
        
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
