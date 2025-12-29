from langchain_core.tools import tool
from linkup import LinkupClient
import os
import logging
from config import *

logger = logging.getLogger(__name__)

@tool
def linkup_search(query: str) -> dict:
    """Linkup deep search."""
    try:
        client = LinkupClient(api_key=LINKUP_API_KEY)
        response = client.search(
            query=query,
            # depth="deep",
            depth="standard",
            output_type="searchResults"
        )
        # Updated to use object attributes per SDK v0.9.0
        results = getattr(response, 'results', getattr(response, 'sources', []))
        content = "\n".join([f"{r.name}: {getattr(r, 'content', '')}" for r in results])
        sources = [{"url": r.url, "title": r.name, "snippet": getattr(r, 'content', '')} for r in results]
        return {"content": content, "sources": sources}
    except Exception as e:
        logger.error(f"Error in linkup_search: {e}")  # Log API or network errors for debugging
        mock_content = f"Mock linkup_search('{query}'): Searched: Top papers on IO economics... Note: LINKUP_API_KEY required. Error: {str(e)[:300]}"
        mock_sources = [{"url": "https://example.com", "title": "Mock Search Result", "snippet": "Mock snippet from search"}]
        return {"content": mock_content, "sources": mock_sources}