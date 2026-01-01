from langchain_core.tools import tool
import os
import logging
import time
import random
import requests
from requests.exceptions import Timeout, HTTPError
from config import *
from tavily import TavilyClient

logger = logging.getLogger(__name__)

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
]

@tool
def tavily_extract(url: str, extract_depth: str = "basic", format: str = "markdown") -> dict:
    """Tavily web content extraction with anti-bot headers and fallback."""
    try:
        # URL validation
        try:
            headers = {"User-Agent": random.choice(user_agents)}
            resp = requests.head(url, headers=headers, timeout=5)
            if resp.status_code not in [200, 302, 303]:
                raise ValueError(f"Invalid URL: {url} returned {resp.status_code}")
        except requests.RequestException as e:
            raise ValueError(f"URL validation failed for {url}: {e}")

        # Retry loop with backoff
        response = None
        for attempt in range(3):
            try:
                client = TavilyClient(api_key=TAVILY_API_KEY)
                response = client.extract(urls=[url], extract_depth=extract_depth, format=format)
                break
            except (Timeout, HTTPError) as e:
                if attempt < 2:
                    time.sleep(2 ** attempt)  # exponential backoff
                    continue
                else:
                    raise

        if response and response.get('results') and len(response['results']) > 0:
            raw_content = response['results'][0]['raw_content']
            sources = [{"url": url, "title": "Extracted Content", "snippet": raw_content[:200]}]
            if 'failed_results' in response and response['failed_results']:
                logger.warning(f"Failed results for {url}: {response['failed_results']}")
            return {"content": raw_content, "sources": sources}
        else:
            failed = response.get('failed_results', []) if response else []
            if failed:
                logger.error(f"Extraction failed for {url}: {failed}")
                raise ValueError(f"Extraction failed for some URLs: {failed}")
            else:
                raise ValueError("Empty results from Tavily extract")
    except Exception as e:
        logger.error(f"Error in tavily_extract: {e}")
        # Fallback to linkup_fetch
        try:
            from tools.linkup_fetch import linkup_fetch
            fallback_result = linkup_fetch.invoke({"url": url})
            return fallback_result
        except Exception as fallback_e:
            logger.error(f"Fallback failed: {fallback_e}")
            mock_content = f"Mock tavily_extract('{url}'): Extracted markdown: # Title\nContent... Error: {str(e)[:300]}"
            mock_sources = [{"url": url, "title": "Mock Extracted Title", "snippet": "Mock snippet"}]
            return {"content": mock_content, "sources": mock_sources}

# Temporary test block
# result = tavily_extract("https://example.com/protected.pdf")
# print(result)