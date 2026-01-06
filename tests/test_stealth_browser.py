import pytest
from tools.stealth_browser import stealth_scrape

def test_stealth_scrape_example():
    """Test stealth scraping on example.com"""
    url = "https://example.com"
    try:
        result = stealth_scrape(url)
        assert result is not None
        assert "content" in result
        assert "Example Domain" in result["content"]
        assert "sources" in result
        assert result["sources"][0]["url"] == url
    except Exception as e:
        pytest.fail(f"Stealth scrape failed: {e}")
