from langchain_core.tools import tool
from linkup import LinkupClient
import os
import logging
from config import *

logger = logging.getLogger(__name__)

@tool
def linkup_fetch(url: str) -> dict:
    """Linkup fetch content from URL."""
    try:
        client = LinkupClient(api_key=LINKUP_API_KEY)
        response = client.fetch(url=url)
        # Updated to use SDK v0.9.0; fetch returns content string or object with .content
        content = response if isinstance(response, str) else getattr(response, 'content', str(response))
        sources = [{"url": url, "title": "Fetched Content", "snippet": content[:200]}]
        return {"content": content, "sources": sources}
    except Exception as e:
        logger.error(f"Error in linkup_fetch: {e}")  # Log API errors for debugging
        mock_content = f"Mock linkup_fetch('{url}'): Fetched: Detailed case summary from courtlistener.com... Note: LINKUP_API_KEY required. Error: {str(e)[:300]}"
        mock_sources = [{"url": url, "title": "Mock Fetched Title", "snippet": "Mock snippet from fetch"}]
        return {"content": mock_content, "sources": mock_sources}