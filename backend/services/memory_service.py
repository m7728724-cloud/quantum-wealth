"""Adaptive Memory Service - RAG-style memory for AI"""
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pymongo import MongoClient, DESCENDING
import os

logger = logging.getLogger(__name__)


def get_db():
    """Get MongoDB database connection"""
    from dotenv import load_dotenv
    load_dotenv()
    client = MongoClient(os.environ.get("MONGO_URL", "mongodb://localhost:27017"))
    return client[os.environ.get("DB_NAME", "quantum_wealth")]


def retrieve_relevant_memories(
    db,
    interaction_type: Optional[str] = None,
    tags: List[str] = None,
    limit: int = 20
) -> List[Dict]:
    """Retrieve relevant memories for AI context (RAG-style)"""
    query = {}
    if interaction_type:
        query["interaction_type"] = interaction_type
    if tags:
        query["tags"] = {"$in": tags}
    
    memories = list(
        db.memory.find(query)
        .sort("created_at", DESCENDING)
        .limit(limit)
    )
    
    return [_serialize(m) for m in memories]


def retrieve_safeguard_rules(db, active_only: bool = True) -> List[Dict]:
    """Get active safeguard rules"""
    query = {}
    if active_only:
        query["active"] = True
    
    rules = list(
        db.safeguard_rules.find(query)
        .sort("created_at", DESCENDING)
    )
    return [_serialize(r) for r in rules]


def log_memory(
    db,
    interaction_type: str,
    content: str,
    outcome: Optional[str] = None,
    tags: List[str] = None,
    user_id: Optional[str] = None
) -> Dict:
    """Log a memory entry"""
    entry = {
        "interaction_type": interaction_type,
        "content": content,
        "outcome": outcome,
        "tags": tags or [],
        "user_id": user_id,
        "created_at": datetime.now().isoformat(),
    }
    result = db.memory.insert_one(entry)
    entry["_id"] = str(result.inserted_id)
    return entry


def save_safeguard_rules(db, rules: List[Dict], user_id: Optional[str] = None) -> List[Dict]:
    """Save AI-generated safeguard rules"""
    saved = []
    for rule in rules:
        if "error" in rule:
            continue
        doc = {
            "user_id": user_id,
            "rule_text": rule.get("rule_text", ""),
            "severity": rule.get("severity", "medium"),
            "confidence": rule.get("confidence", 0.5),
            "pattern_found": rule.get("pattern_found", ""),
            "related_assets": rule.get("related_assets", []),
            "source": "ai_generated",
            "active": True,
            "created_at": datetime.now().isoformat(),
        }
        result = db.safeguard_rules.insert_one(doc)
        doc["_id"] = str(result.inserted_id)
        saved.append(doc)
    return saved


def _serialize(doc: Dict) -> Dict:
    """Serialize MongoDB document"""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc
