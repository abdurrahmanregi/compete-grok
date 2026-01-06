import pytest
from unittest.mock import MagicMock, patch
from tools.fetch_paper import fetch_paper_content

@pytest.fixture
def mock_convert_pdf_url():
    with patch('tools.fetch_paper.convert_pdf_url') as mock:
        yield mock

@pytest.fixture
def mock_tavily_search():
    with patch('tools.fetch_paper.tavily_search') as mock:
        yield mock

@pytest.fixture
def mock_tavily_extract():
    with patch('tools.fetch_paper.tavily_extract') as mock:
        yield mock

def test_fetch_paper_direct_pdf_success(mock_convert_pdf_url):
    mock_convert_pdf_url.invoke.return_value = {"success": True, "content": "PDF Content with DOI: 10.1234/5678"}
    
    result = fetch_paper_content.invoke({"url": "http://example.com/paper.pdf"})
    
    assert result["content"] == "PDF Content with DOI: 10.1234/5678"
    assert result["source"] == "http://example.com/paper.pdf"
    assert result["doi"] == "10.1234/5678"
    mock_convert_pdf_url.invoke.assert_called_once_with({"url": "http://example.com/paper.pdf"})

def test_fetch_paper_direct_pdf_failure_alt_search_success(mock_convert_pdf_url, mock_tavily_search):
    # First call fails
    mock_convert_pdf_url.invoke.side_effect = [
        {"success": False, "error": "403 Forbidden"}, # First call for original URL
        {"success": True, "content": "Alternative PDF Content"} # Second call for alt URL
    ]
    
    # Mock search result
    mock_tavily_search.invoke.return_value = {
        "sources": [
            {"url": "http://example.com/alt_paper.pdf"}
        ]
    }
    
    result = fetch_paper_content.invoke({"url": "http://example.com/paper.pdf", "title": "Test Paper"})
    
    assert result["content"] == "Alternative PDF Content"
    assert result["source"] == "http://example.com/alt_paper.pdf"
    assert mock_convert_pdf_url.invoke.call_count == 2
    mock_tavily_search.invoke.assert_called()

def test_fetch_paper_html_fallback(mock_convert_pdf_url, mock_tavily_search, mock_tavily_extract):
    # PDF conversion fails
    mock_convert_pdf_url.invoke.return_value = {"success": False, "error": "Failed"}
    # Search returns no useful PDFs
    mock_tavily_search.invoke.return_value = {"sources": []}
    # HTML extraction succeeds
    long_content = "HTML Content of the paper " * 10  # Make it > 100 chars
    mock_tavily_extract.invoke.return_value = {"content": long_content}
    
    result = fetch_paper_content.invoke({"url": "http://example.com/paper.pdf"})
    
    assert result["content"] == long_content
    assert result["status"] == "fallback_html"
    mock_tavily_extract.invoke.assert_called_once_with({"url": "http://example.com/paper.pdf"})

def test_fetch_paper_non_pdf_url(mock_tavily_extract):
    long_content = "HTML Content " * 20 # Make it > 100 chars
    mock_tavily_extract.invoke.return_value = {"content": long_content}
    
    result = fetch_paper_content.invoke({"url": "http://example.com/paper.html"})
    
    # Should skip direct PDF and go to alt search (which we mock to fail/skip) then HTML fallback
    # Wait, my implementation for non-pdf URL:
    # 1. is_pdf_url = False -> Skips direct PDF
    # 2. Alt search runs (might find nothing)
    # 3. HTML fallback runs
    
    # Let's mock search to return nothing to ensure it hits HTML fallback
    with patch('tools.fetch_paper.tavily_search') as mock_search:
        mock_search.invoke.return_value = {"sources": []}
        
        result = fetch_paper_content.invoke({"url": "http://example.com/paper.html"})
        
        assert result["content"] == long_content
        assert result["status"] == "fallback_html"
