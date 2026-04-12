"""RSS News Aggregation Service"""
import feedparser
import logging
from datetime import datetime
from typing import List, Dict, Any
import hashlib

logger = logging.getLogger(__name__)

FEED_SOURCES = [
    {"name": "Yahoo Finance", "url": "https://finance.yahoo.com/news/rssindex", "region": "global"},
    {"name": "Investing.com", "url": "https://www.investing.com/rss/news.rss", "region": "global"},
    {"name": "RBC.ru", "url": "https://rssexport.rbc.ru/rbcnews/news/30/full.rss", "region": "russia"},
    {"name": "MOEX News", "url": "https://www.moex.com/export/news.aspx?cat=100", "region": "russia"},
]


def fetch_all_feeds(max_per_feed: int = 10) -> List[Dict[str, Any]]:
    """Fetch and normalize articles from all RSS feeds"""
    all_articles = []
    
    for feed_info in FEED_SOURCES:
        try:
            parsed = feedparser.parse(feed_info["url"])
            
            if parsed.bozo and not parsed.entries:
                logger.warning(f"Feed error for {feed_info['name']}: {getattr(parsed, 'bozo_exception', 'unknown')}")
                continue
            
            entries = parsed.entries[:max_per_feed]
            
            for entry in entries:
                title = entry.get("title", "").strip()
                if not title:
                    continue
                
                article = {
                    "source": feed_info["name"],
                    "region": feed_info["region"],
                    "title": title,
                    "link": entry.get("link", ""),
                    "published": entry.get("published", entry.get("updated", "")),
                    "summary": _clean_summary(entry.get("summary", "")),
                    "hash": hashlib.md5(title.encode()).hexdigest()[:12],
                    "fetched_at": datetime.now().isoformat()
                }
                all_articles.append(article)
            
            logger.info(f"Fetched {len(entries)} articles from {feed_info['name']}")
        
        except Exception as e:
            logger.error(f"Error fetching {feed_info['name']}: {e}")
    
    # Deduplicate by hash
    seen = set()
    unique = []
    for art in all_articles:
        if art["hash"] not in seen:
            seen.add(art["hash"])
            unique.append(art)
    
    # Sort by fetched_at descending
    unique.sort(key=lambda x: x.get("fetched_at", ""), reverse=True)
    
    return unique


def _clean_summary(summary: str) -> str:
    """Clean HTML from summary"""
    if not summary:
        return ""
    import re
    clean = re.sub(r'<[^>]+>', '', summary)
    clean = clean.strip()[:300]
    return clean
