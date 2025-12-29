from functools import lru_cache
from tenacity import retry, stop_after_attempt, wait_exponential
from .tavily_search import tavily_search as _tavily_search
from .linkup_search import linkup_search as _linkup_search
from .linkup_fetch import linkup_fetch as _linkup_fetch
from .tavily_extract import tavily_extract as _tavily_extract
from .convert_pdf_url import convert_pdf_url as _convert_pdf_url


class ToolExecutionError(Exception):
    """Custom exception for tool execution failures after retries."""
    pass


@lru_cache(maxsize=128)
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def tavily_search(query: str, time_range: str = "year") -> dict:
    result = _tavily_search(query, time_range)
    if "Mock" in result.get("content", ""):
        raise ToolExecutionError(f"tavily_search failed: {result['content']}")
    return result


@lru_cache(maxsize=128)
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def linkup_search(query: str) -> dict:
    result = _linkup_search(query)
    if "Mock" in result.get("content", ""):
        raise ToolExecutionError(f"linkup_search failed: {result['content']}")
    return result


@lru_cache(maxsize=128)
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def linkup_fetch(url: str) -> dict:
    result = _linkup_fetch(url)
    if "Mock" in result.get("content", ""):
        raise ToolExecutionError(f"linkup_fetch failed: {result['content']}")
    return result


@lru_cache(maxsize=128)
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def tavily_extract(url: str) -> dict:
    result = _tavily_extract(url)
    if "Mock" in result.get("content", ""):
        raise ToolExecutionError(f"tavily_extract failed: {result['content']}")
    return result


@lru_cache(maxsize=128)
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def convert_pdf_url(url: str) -> str:
    result = _convert_pdf_url(url)
    if "Mock" in result:
        raise ToolExecutionError(f"convert_pdf_url failed: {result}")
    return result