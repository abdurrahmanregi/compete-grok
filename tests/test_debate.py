import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from unittest.mock import patch, MagicMock
from debate import pro_node, cons_node, arbiter_node

def test_pro_node():
    """Test pro debate node."""
    state = {"messages": [MagicMock()]}
    with patch('debate.agents') as mock_agents:
        mock_agent = MagicMock()
        mock_agent.invoke.return_value = {"messages": ["pro response"]}
        mock_agents.__getitem__.return_value = mock_agent

        result = pro_node(state)
        assert result["messages"] == ["pro response"]

def test_cons_node():
    """Test cons debate node."""
    state = {"messages": [MagicMock()]}
    with patch('debate.agents') as mock_agents:
        mock_agent = MagicMock()
        mock_agent.invoke.return_value = {"messages": ["cons response"]}
        mock_agents.__getitem__.return_value = mock_agent

        result = cons_node(state)
        assert result["messages"] == ["cons response"]

def test_arbiter_node():
    """Test arbiter debate node increments round."""
    state = {"messages": [MagicMock()], "debate_round": 0}
    with patch('debate.agents') as mock_agents:
        mock_agent = MagicMock()
        mock_agent.invoke.return_value = {"messages": ["arbiter response"]}
        mock_agents.__getitem__.return_value = mock_agent

        result = arbiter_node(state)
        assert result["messages"] == ["arbiter response"]
        assert result["debate_round"] == 1