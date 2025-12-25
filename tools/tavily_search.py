from langchain_core.tools import tool
from tavily import TavilyClient
import os
from config import *

@tool
def tavily_search(query: str, time_range: str = "year") -> dict:
    """Tavily broad search for recent econ papers/news."""
    try:
        client = TavilyClient(api_key=TAVILY_API_KEY)
        response = client.search(
            query=query,
            search_depth="basic",
            max_results=TAVILY_MAX_RESULTS,
            time_range=time_range
        )
        results = response.get("results", [])
        content = "\n".join([f"{r['title']}: {r['content']}" for r in results])
        sources = [{"url": r["url"], "title": r["title"], "snippet": r["content"]} for r in results]
        return {"content": content, "sources": sources}
    except Exception as e:
        mock_content = f"Mock tavily_search('{query}'): Searched: Top papers on IO economics... Note: TAVILY_API_KEY required. Error: {str(e)[:300]}"
        mock_sources = [{"url": "https://example.com", "title": "Mock Search Result", "snippet": "Mock snippet from search"}]
        return {"content": mock_content, "sources": mock_sources}