import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def search_medical_web(query: str, max_results: int = 3) -> List[Dict[str, Any]]:
    """
    Executes a web search for medical information using DuckDuckGo.
    Returns grounded clinical web snippets with source URLs.
    """
    try:
        from duckduckgo_search import DDGS
        # Enhance query with medical context keywords to focus on clinical sources
        enhanced_query = f"{query} medical health guidelines"
        with DDGS() as ddgs:
            raw_results = list(ddgs.text(enhanced_query, max_results=max_results))
            if not raw_results:
                raw_results = list(ddgs.text(query, max_results=max_results))
            
        results = []
        for item in raw_results:
            results.append({
                "title": item.get("title", "Web Medical Reference"),
                "url": item.get("href", ""),
                "snippet": item.get("body", ""),
                "source_type": "web"
            })
        logger.info(f"Retrieved {len(results)} live web search results for '{query}'")
        return results
    except Exception as e:
        logger.warning(f"Web search failed or timed out: {e}")
        return []
