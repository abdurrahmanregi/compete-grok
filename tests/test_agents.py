import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from unittest.mock import patch, MagicMock
from agents.supervisor import create_supervisor_agent, SUPERVISOR_PROMPT, SUPERVISOR_TOOLS
from agents import create_agent

def test_create_supervisor_agent():
    """Test creation of supervisor agent."""
    with patch('agents.supervisor.create_agent') as mock_create:
        mock_agent = MagicMock()
        mock_create.return_value = mock_agent

        result = create_supervisor_agent()
        mock_create.assert_called_once()
        args = mock_create.call_args
        assert args[0][0] == "supervisor"
        assert SUPERVISOR_PROMPT in args[0][2]
        assert SUPERVISOR_TOOLS == args[0][3]

def test_create_agent_basic():
    """Test basic agent creation."""
    with patch('agents.create_react_agent') as mock_create:
        mock_agent = MagicMock()
        mock_create.return_value = mock_agent

        result = create_agent("test_agent", "test_model", "test_prompt", [])
        mock_create.assert_called_once()
        # Verify parameters passed correctly

def test_supervisor_prompt_content():
    """Test that supervisor prompt contains key elements."""
    assert "Managing Partner" in SUPERVISOR_PROMPT
    assert "jurisdictional specificity" in SUPERVISOR_PROMPT.lower()
    assert "consumer welfare" in SUPERVISOR_PROMPT.lower()
    assert "evidence hierarchy" in SUPERVISOR_PROMPT.lower()

def test_supervisor_tools_include_sequential_thinking():
    """Test that supervisor tools include sequential thinking."""
    tool_names = [tool.name for tool in SUPERVISOR_TOOLS]
    assert "sequential_thinking" in tool_names