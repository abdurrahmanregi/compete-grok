import pytest
from unittest.mock import patch

# Shared fixtures for mocking API keys and configuration in tests
# Use in tests: def test_something(mock_api_keys, mock_strict_mode): ...

@pytest.fixture(scope='function')
def mock_api_keys():
    """Mock all API keys and environment variables used in config.py"""
    with patch.dict('os.environ', {
        'XAI_API_KEY': 'mock_xai',
        'TAVILY_API_KEY': 'mock_tavily',
        'MISTRAL_API_KEY': 'mock_mistral',
        'LINKUP_API_KEY': 'mock_linkup',
        'LANGCHAIN_API_KEY': 'mock_langchain',
        'LANGCHAIN_TRACING_V2': 'mock_tracing',
        'LANGCHAIN_PROJECT': 'mock_project',
        'VERBOSE': 'false'
    }):
        yield

@pytest.fixture(scope='function')
def mock_strict_mode():
    """Mock STRICT_MODE to False for tests to avoid real tool executions"""
    with patch('config.STRICT_MODE', False):
        yield