from langchain_core.tools import tool
from .convert_pdf_url import convert_pdf_url
from .tavily_search import tavily_search
from .tavily_extract import tavily_extract
import logging
import re
import urllib.parse

logger = logging.getLogger(__name__)

@tool
def fetch_paper_content(url: str, title: str = "", authors: str = "") -> dict:
    """
    Robustly fetch paper content with fallback strategy:
    1. Direct PDF (convert_pdf_url)
    2. Alternative Search (Pre-print/Author Site via Tavily)
    3. HTML Fallback (tavily_extract)
    
    Args:
        url: The primary URL to fetch.
        title: The title of the paper (optional, used for alternative search).
        authors: The authors of the paper (optional, used for alternative search).
        
    Returns:
        dict: {"content": "...", "source": "...", "doi": "..."} or error.
    """
    
    # Helper to extract DOI
    def extract_doi(text):
        if not text:
            return None
        # Common DOI regex patterns
        doi_pattern = r'\b(10\.\d{4,9}/[-._;()/:A-Z0-9]+)\b'
        match = re.search(doi_pattern, text, re.IGNORECASE)
        return match.group(1) if match else None

    # Helper to extract title from URL if not provided
    def extract_title_from_url(url_str):
        try:
            path = urllib.parse.urlparse(url_str).path
            filename = path.split('/')[-1]
            # Remove extension and replace separators with spaces
            name = re.sub(r'\.[^.]+$', '', filename)
            return name.replace('-', ' ').replace('_', ' ')
        except Exception:
            return "unknown paper"

    # 1. Try Direct PDF
    # Check if URL ends with .pdf or we have strong reason to believe it's a PDF
    try:
        is_pdf_url = url.lower().endswith('.pdf')
        
        if is_pdf_url:
            logger.info(f"Attempting direct PDF conversion for {url}")
            try:
                result = convert_pdf_url.invoke({"url": url})
                
                if isinstance(result, dict) and result.get('success'):
                    content = result.get('content', "")
                    return {
                        "content": content, 
                        "source": url, 
                        "doi": extract_doi(content)
                    }
            except Exception as e:
                logger.warning(f"Direct PDF conversion failed for {url}: {e}")
    except Exception as e:
        logger.warning(f"Error checking PDF URL: {e}")
    
    # 2. Alternative Search (Fallback)
    # If direct PDF failed or wasn't a PDF URL, but we suspect it's a paper
    # We only do this if we have a title or can derive one, or if the original URL failed
    logger.info("Attempting alternative search (Pre-print/Author Site)...")
    
    if not title:
        title = extract_title_from_url(url)
    
    # Construct queries to find free versions
    queries = [
        f'"{title}" filetype:pdf',
        f'"{title}" {authors} (NBER OR SSRN OR IZA OR "Working Paper")',
        f'"{title}" {authors} site:.edu'
    ]
    
    for query in queries:
        try:
            # Use a restrictive time range to get recent versions if possible, but default is fine
            search_res = tavily_search.invoke({"query": query})
            
            if isinstance(search_res, dict) and "sources" in search_res:
                for source in search_res['sources']:
                    alt_url = source.get('url')
                    # We are looking for PDFs specifically in this step
                    if alt_url and alt_url.lower().endswith('.pdf') and alt_url != url:
                        logger.info(f"Found alternative PDF: {alt_url}")
                        try:
                            res = convert_pdf_url.invoke({"url": alt_url})
                            if isinstance(res, dict) and res.get('success'):
                                content = res.get('content', "")
                                return {
                                    "content": content, 
                                    "source": alt_url, 
                                    "doi": extract_doi(content)
                                }
                        except Exception as e:
                            logger.warning(f"Alternative PDF conversion failed for {alt_url}: {e}")
        except Exception as e:
            logger.warning(f"Alternative search query '{query}' failed: {e}")
            continue

    # 3. HTML Fallback
    # If we are here, Direct PDF failed (or wasn't PDF) and Alt Search failed to find a PDF.
    # Try to extract content from the original URL using Tavily Extract.
    logger.info(f"Falling back to HTML extraction for {url}...")
    try:
        html_res = tavily_extract.invoke({"url": url})
        content = html_res.get('content', "")
        
        if content and "Mock" not in content and len(content) > 100:
             return {
                "content": content,
                "source": url,
                "doi": extract_doi(content),
                "status": "fallback_html"
            }
    except Exception as e:
        logger.warning(f"HTML extraction failed: {e}")

    # 4. Error Handling
    return {
        "content": "Failed to retrieve content. Direct PDF conversion failed, alternative PDF search yielded no results, and HTML extraction failed.",
        "source": url,
        "doi": None,
        "error": True
    }
