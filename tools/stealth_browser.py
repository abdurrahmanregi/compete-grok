from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from fake_useragent import UserAgent
import logging

logger = logging.getLogger(__name__)

def stealth_scrape(url: str) -> dict:
    """
    Scrapes a URL using Playwright with stealth settings to bypass 403/bot detection.
    Returns a dictionary with 'content' and 'sources' keys, matching tavily_extract interface.
    """
    ua = UserAgent()
    user_agent = ua.random
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent=user_agent)
            page = context.new_page()
            
            # Apply stealth
            stealth = Stealth()
            stealth.apply_stealth_sync(page)
            
            logger.info(f"Stealth scraping {url} with UA: {user_agent}")
            
            # Navigate
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                # Wait a bit for dynamic content if needed
                page.wait_for_selector("body", timeout=10000)
            except Exception as nav_e:
                logger.warning(f"Navigation warning for {url}: {nav_e}")
                # Continue to try extracting content even if timeout occurred, as some content might be loaded
            
            # Extract content
            content = page.evaluate("document.body.innerText")
            title = page.title()
            
            browser.close()
            
            if not content or not content.strip():
                raise ValueError("Empty content extracted")

            return {
                "content": content,
                "sources": [{"url": url, "title": title, "snippet": content[:200] if content else ""}]
            }
            
    except Exception as e:
        logger.error(f"Stealth scrape failed for {url}: {e}")
        raise e
