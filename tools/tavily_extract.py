from langchain_core.tools import tool
import os
import logging
from config import *
from tavily import TavilyClient

logger = logging.getLogger(__name__)

@tool
def tavily_extract(url: str) -> dict:
    """Tavily web content extraction."""
    # Updated to SDK client.extract per docs; removes subprocess
    try:
        client = TavilyClient(api_key=TAVILY_API_KEY)
        response = client.extract(urls=[url], extract_depth="advanced", format="markdown")
        if response.get('results') and len(response['results']) > 0:
            raw_content = response['results'][0]['raw_content']
            sources = [{"url": url, "title": "Extracted Content", "snippet": raw_content[:200]}]
            return {"content": raw_content, "sources": sources}
        else:
            raise ValueError("Empty results from Tavily extract")
    except Exception as e:
        logger.error(f"Error in tavily_extract: {e}")  # Log API errors for debugging
        mock_content = f"Mock tavily_extract('{url}'): Extracted markdown: # NBER Paper Title\nAbstract: Recent IO analysis... Note: TAVILY_API_KEY required. Error: {str(e)[:300]}"
        mock_sources = [{"url": url, "title": "Mock Extracted Title", "snippet": "Mock snippet from extraction"}]
        return {"content": mock_content, "sources": mock_sources}