from langchain_core.tools import tool
from .convert_pdf_url import convert_pdf_url
from .tavily_search import tavily_search
from .tavily_extract import tavily_extract
from .linkup_fetch import linkup_fetch
import logging
import time
import re

logger = logging.getLogger(__name__)

@tool
def fetch_paper_content(url: str, title: str = "", authors: str = "") -> dict:
    """
    Robustly fetch paper content from a URL.
    If the URL is a PDF and fails (e.g., 403), it searches for alternative URLs.
    If it's not a PDF, it uses extraction.
    
    Args:
        url: The primary URL to fetch.
        title: The title of the paper (optional, used for alternative search).
        authors: The authors of the paper (optional, used for alternative search).
        
    Returns:
        dict: {"content": "...", "source": "..."} or error.
    """
    try:
        is_pdf = url.lower().endswith('.pdf')
        
        if is_pdf:
            try:
                # Note: convert_pdf_url returns a dict or str depending on implementation.
                # The current implementation in tools/convert_pdf_url.py returns a dict.
                result = convert_pdf_url(url)
                
                if isinstance(result, dict) and result.get("success"):
                    return {"content": result["content"], "source": url}
                
                # Handle 403 or failure
                if isinstance(result, dict) and (result.get("error") == "403 Forbidden" or not result.get("success")):
                    logger.info(f"PDF fetch failed for {url}. Attempting alternative search.")
                    if not title:
                        # Try to extract title from URL
                        match = re.search(r'/([^/]+)\.pdf', url)
                        title = match.group(1) if match else "unknown paper"
                    
                    # Search for alternatives
                    # Construct a more robust query including authors and working paper keywords
                    author_part = f"{authors} " if authors else ""
                    query = f'"{title}" {author_part}(NBER OR SSRN OR "working paper") filetype:pdf'
                    
                    try:
                        search_res = tavily_search(query, time_range="year")
                        
                        # Try alternatives
                        if isinstance(search_res, dict) and "sources" in search_res:
                            for source in search_res["sources"]:
                                alt_url = source.get("url")
                                if alt_url and alt_url != url and alt_url.lower().endswith('.pdf'):
                                    logger.info(f"Trying alternative URL: {alt_url}")
                                    try:
                                        alt_res = convert_pdf_url(alt_url)
                                        if isinstance(alt_res, dict) and alt_res.get("success"):
                                            return {"content": alt_res["content"], "source": alt_url}
                                    except Exception:
                                        continue
                    except Exception as e:
                        logger.warning(f"Alternative search failed: {e}")
                
                # If PDF conversion failed or no alternatives found, try HTML extraction as final fallback
                logger.info(f"PDF conversion failed for {url} and alternatives. Attempting HTML extraction as final fallback.")
                try:
                    # Try extracting from the original URL first
                    html_res = tavily_extract(url)
                    content = html_res.get("content", "")
                    if content and "Mock" not in content and len(content) > 100:
                        return {"content": f"[HTML Fallback] {content}", "source": url}
                    
                    # If original URL fails, and we had an alternative URL, try that
                    # (This logic would require tracking the best alternative URL, which we might not have easily here without refactoring)
                    # For now, just falling back to original URL HTML extraction is a good step.
                except Exception as html_e:
                    logger.warning(f"HTML fallback failed: {html_e}")

                error_msg = result.get('error') if isinstance(result, dict) else str(result)
                return {"content": f"Failed to retrieve PDF content for {url}. Error: {error_msg}. HTML fallback also failed.", "source": url}
                
            except Exception as e:
                 return {"content": f"Error processing PDF {url}: {e}", "source": url}
        else:
            # Not a PDF, use extract
            try:
                # Try tavily_extract first
                res = tavily_extract(url)
                content = res.get("content", "")
                if content and "Mock" not in content and len(content) > 100:
                     return {"content": content, "source": url}
                
                # Fallback to linkup_fetch
                logger.info(f"Tavily extract failed or empty for {url}, trying Linkup.")
                res = linkup_fetch(url)
                return {"content": res.get("content", ""), "source": url}
            except Exception as e:
                return {"content": f"Error extracting {url}: {e}", "source": url}
    except Exception as e:
        return {"success": False, "error": str(e)}
