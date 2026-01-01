import pytest
from unittest.mock import MagicMock, patch
from tools.tavily_extract import tavily_extract

def test_tavily_extract_fallback_success():
    """
    Test that tavily_extract falls back to linkup_fetch when TavilyClient fails.
    """
    url = "https://example.com/test"
    
    # Mock requests.head to pass validation
    with patch("requests.head") as mock_head:
        mock_head.return_value.status_code = 200
        
        # Mock TavilyClient to raise an exception
        with patch("tools.tavily_extract.TavilyClient") as mock_tavily_client:
            # The TavilyClient constructor is called, then .extract()
            mock_instance = mock_tavily_client.return_value
            mock_instance.extract.side_effect = Exception("Tavily API failure")
            
            # Mock linkup_fetch
            # Since it is imported inside the function, we need to patch the module where it comes from.
            with patch("tools.linkup_fetch.linkup_fetch") as mock_linkup_tool:
                # Configure the mock tool to behave like a StructuredTool (callable via invoke)
                expected_result = {"content": "Fallback content", "sources": [{"url": url, "title": "Fallback", "snippet": "..."}]}
                mock_linkup_tool.invoke.return_value = expected_result
                
                # Run the function via invoke
                result = tavily_extract.invoke({"url": url})
                
                # Verify TavilyClient.extract was called (and failed)
                mock_instance.extract.assert_called()
                
                # Verify linkup_fetch.invoke was called
                mock_linkup_tool.invoke.assert_called_once_with({"url": url})
                
                # Verify result matches fallback result
                assert result == expected_result

def test_tavily_extract_fallback_failure():
    """
    Test that if fallback also fails, it returns the mock error response.
    """
    url = "https://example.com/test"
    
    with patch("requests.head") as mock_head:
        mock_head.return_value.status_code = 200
        
        with patch("tools.tavily_extract.TavilyClient") as mock_tavily_client:
            mock_instance = mock_tavily_client.return_value
            mock_instance.extract.side_effect = Exception("Tavily API failure")
            
            with patch("tools.linkup_fetch.linkup_fetch") as mock_linkup_tool:
                # Make fallback fail too
                mock_linkup_tool.invoke.side_effect = Exception("Linkup failure")
                
                result = tavily_extract.invoke({"url": url})
                
                # Verify fallback was attempted
                mock_linkup_tool.invoke.assert_called_once()
                
                # Verify final mock response
                assert "Mock tavily_extract" in result["content"]
                # The error message in the mock content comes from the original exception (Tavily API failure)
                assert "Tavily API failure" in result["content"]
