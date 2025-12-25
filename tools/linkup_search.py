from langchain_core.tools import tool
from linkup import LinkupClient
import os
from config import *

@tool
def linkup_search(query: str) -> dict:
    """Linkup deep search."""
    try:
        client = LinkupClient(api_key=LINKUP_API_KEY)
        response = client.search(
            query=query,
            depth="deep",
            output_type="searchResults"
        )
        results = response.get("sources", response.get("results", []))
        content = "\n".join([f"{r['name']}: {r['snippet']}" for r in results])
        sources = [{"url": r["url"], "title": r["name"], "snippet": r["snippet"]} for r in results]
        return {"content": content, "sources": sources}
    except Exception as e:
        mock_content = f"Mock linkup_search('{query}'): Searched: Top papers on IO economics... Note: LINKUP_API_KEY required. Error: {str(e)[:300]}"
        mock_sources = [{"url": "https://example.com", "title": "Mock Search Result", "snippet": "Mock snippet from search"}]
        return {"content": mock_content, "sources": mock_sources}