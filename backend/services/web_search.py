"""
Web Search Service.
Uses DuckDuckGo search via duckduckgo_search to retrieve web results.
"""

import logging
import requests
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def search_web(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Search using Wikipedia API and return structured results.
    """
    results = []
    try:
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "utf8": "1",
            "format": "json",
            "srlimit": max_results
        }
        headers = {
            "User-Agent": "MultiAgentResearchSystem/1.0"
        }
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        search_results = data.get("query", {}).get("search", [])
        for item in search_results:
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            # Clean HTML tags from snippet if present (Wikipedia returns HTML snippets)
            snippet = snippet.replace("<span class=\"searchmatch\">", "").replace("</span>", "").replace("&quot;", "\"")
            
            results.append({
                "title": title,
                "url": f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}",
                "snippet": snippet if snippet else f"Wikipedia article about {title}",
            })
                
        logger.info(f"Web search for '{query}' returned {len(results)} results")

    except Exception as e:
        logger.error(f"Web search failed for query '{query}': {e}")
        results = []

    return results

async def async_search_web(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    return search_web(query, max_results=max_results)
