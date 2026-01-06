import pytest
from unittest.mock import patch, MagicMock
from tools.fetch_paper import fetch_paper_content
from agents.econpaper import create_econpaper_agent, ECONPAPER_TOOLS

class TestFetchPaperContent:
    @patch('tools.fetch_paper.convert_pdf_url')
    def test_fetch_paper_content_pdf_success(self, mock_convert):
        """Test successful PDF fetch."""
        # Mock the invoke method since it's a tool
        mock_convert.invoke.return_value = {"success": True, "content": "PDF Content"}
        
        # Use invoke for LangChain tool
        result = fetch_paper_content.invoke({"url": "http://example.com/paper.pdf"})
        
        assert result["content"] == "PDF Content"
        assert result["source"] == "http://example.com/paper.pdf"
        mock_convert.invoke.assert_called_once_with({"url": "http://example.com/paper.pdf"})

    @patch('tools.fetch_paper.convert_pdf_url')
    @patch('tools.fetch_paper.tavily_search')
    def test_fetch_paper_content_pdf_failure_retry(self, mock_search, mock_convert):
        """Test PDF fetch failure (403) triggering alternative search."""
        # First call fails, second call (alternative) succeeds
        # Mock invoke side effects
        mock_convert.invoke.side_effect = [
            {"success": False, "error": "403 Forbidden"}, # Original URL
            {"success": True, "content": "Alternative PDF Content"} # Alternative URL
        ]
        
        mock_search.invoke.return_value = {
            "sources": [{"url": "http://alt.com/paper.pdf"}]
        }
        
        # Use invoke for LangChain tool
        result = fetch_paper_content.invoke({
            "url": "http://example.com/paper.pdf",
            "title": "Test Paper",
            "authors": "Doe, J."
        })
        
        assert result["content"] == "Alternative PDF Content"
        assert result["source"] == "http://alt.com/paper.pdf"
        
        # Verify calls
        assert mock_convert.invoke.call_count == 2
        
        # Verify the search query includes title, authors, and keywords
        # The tool constructs queries list and iterates.
        # We expect at least one search call.
        mock_search.invoke.assert_called()
        args, _ = mock_search.invoke.call_args
        assert "Test Paper" in args[0]["query"]

    @patch('tools.fetch_paper.tavily_extract')
    @patch('tools.fetch_paper.convert_pdf_url')
    @patch('tools.fetch_paper.tavily_search')
    def test_fetch_paper_content_non_pdf(self, mock_search, mock_convert, mock_extract):
        """Test fetching non-PDF content."""
        # Content must be > 100 chars to avoid fallback
        long_content = "Web Page Content " * 10 
        mock_extract.invoke.return_value = {"content": long_content}
        
        # Mock convert to fail (since it's not PDF url, it might skip or fail)
        # If url doesn't end in pdf, convert_pdf_url is NOT called in step 1.
        # But step 2 (alt search) might run.
        mock_search.invoke.return_value = {"sources": []}

        # Use invoke for LangChain tool
        result = fetch_paper_content.invoke({"url": "http://example.com/page"})
        
        assert result["content"] == long_content
        assert result["source"] == "http://example.com/page"
        mock_extract.invoke.assert_called_once_with({"url": "http://example.com/page"})

    @patch('tools.fetch_paper.convert_pdf_url')
    def test_fetch_paper_content_exception_handling(self, mock_convert):
        """Test unhandled exception in fetch_paper_content."""
        # This test expects the enhanced error handling
        # We mock invoke to raise an exception
        mock_convert.invoke.side_effect = Exception("Unexpected error")
        
        # Use invoke for LangChain tool
        # Since the tool catches exceptions in step 1, it proceeds to step 2, then 3, then returns error dict.
        # We need to ensure step 2 and 3 also fail or return nothing to get the final error dict.
        
        with patch('tools.fetch_paper.tavily_search') as mock_search, \
             patch('tools.fetch_paper.tavily_extract') as mock_extract:
            
            mock_search.invoke.side_effect = Exception("Search failed")
            mock_extract.invoke.side_effect = Exception("Extract failed")

            result = fetch_paper_content.invoke({"url": "http://example.com/paper.pdf"})
            
            assert result["error"] is True
            assert "Failed to retrieve content" in result["content"]
            assert result["source"] == "http://example.com/paper.pdf"

class TestEconPaperAgent:
    def test_econpaper_agent_tools(self):
        """Verify EconPaper agent has fetch_paper_content tool."""
        # Check the tool list directly
        tool_names = [tool.name for tool in ECONPAPER_TOOLS]
        assert "fetch_paper_content" in tool_names
