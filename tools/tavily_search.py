from langchain_core.tools import tool
from tavily import TavilyClient
import os
import logging
from config import *

logger = logging.getLogger(__name__)

# Mapping for time_range to handle SDK changes requiring short forms
# Also handles common invalid inputs from LLMs by mapping them to 'year'
TIME_RANGE_MAPPING = {
    "day": "d",
    "week": "w",
    "month": "m",
    "year": "y",
    "d": "d",
    "w": "w",
    "m": "m",
    "y": "y",
    # Common invalid inputs mapped to year
    "2y": "y",
    "5y": "y",
    "10y": "y",
    "all": "y",
    "recent": "m"
}

VALID_TIME_RANGES = {'day', 'week', 'month', 'year', 'd', 'w', 'm', 'y'}

@tool
def tavily_search(query: str, time_range: str = "year") -> dict:
    """Tavily broad search for recent econ papers/news.
    
    Args:
        query: The search query string.
        time_range: The time range for search results. 
                    Valid values: 'day', 'week', 'month', 'year'. 
                    Defaults to 'year'.
    """
    try:
        # Normalize input
        time_range_lower = time_range.lower()
        
        # Check if it's a known mapping (valid or common invalid)
        if time_range_lower in TIME_RANGE_MAPPING:
            mapped_time_range = TIME_RANGE_MAPPING[time_range_lower]
            if time_range_lower not in VALID_TIME_RANGES:
                logger.info(f"Mapped invalid time_range '{time_range}' to '{mapped_time_range}'")
        else:
            # Fallback for completely unknown values
            logger.warning(f"Invalid time_range '{time_range}', defaulting to 'year'")
            mapped_time_range = "y"

        client = TavilyClient(api_key=TAVILY_API_KEY)
        response = client.search(
            query=query,
            search_depth="basic",
            # search_depth="advanced",
            max_results=TAVILY_MAX_RESULTS,
            time_range=mapped_time_range
        )
        results = response.get("results", [])
        content = "\n".join([f"{r['title']}: {r['content']}" for r in results])
        sources = [{"url": r["url"], "title": r["title"], "snippet": r["content"]} for r in results]
        return {"content": content, "sources": sources}
    except Exception as e:
        logger.error(f"Error in tavily_search: {e}")  # Log API or network errors for debugging
        mock_content = f"Mock tavily_search('{query}'): Searched: Top papers on IO economics... Note: TAVILY_API_KEY required. Error: {str(e)[:300]}"
        mock_sources = [{"url": "https://example.com", "title": "Mock Search Result", "snippet": "Mock snippet from search"}]
        return {"content": mock_content, "sources": mock_sources}
