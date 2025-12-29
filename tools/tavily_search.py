from langchain_core.tools import tool
from tavily import TavilyClient
import os
import logging
from config import *

logger = logging.getLogger(__name__)

# Mapping for time_range to handle SDK changes requiring short forms
TIME_RANGE_MAPPING = {
    "day": "d",
    "week": "w",
    "month": "m",
    "year": "y"
}

@tool
def tavily_search(query: str, time_range: str = "y") -> dict:
    """Tavily broad search for recent econ papers/news."""
    try:
        # Map long form time_range to short form if needed
        mapped_time_range = TIME_RANGE_MAPPING.get(time_range, time_range)
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