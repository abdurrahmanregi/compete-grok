import pytest
from unittest.mock import MagicMock, patch
import json
from langchain_core.messages import HumanMessage, AIMessage
from debate import debate_app, DebateState

def test_debate_logic_loop():
    """
    Test the debate logic loop: Pro -> Cons -> Arbiter -> (Loop) -> Pro -> Cons -> Arbiter -> End.
    Mocks arbiter to return should_continue=True then False.
    """
    
    with patch.dict('agents.agents', clear=False) as mock_agents:
        
        # Replace real agents with Mocks
        mock_agents["pro"] = MagicMock()
        mock_agents["cons"] = MagicMock()
        mock_agents["arbiter"] = MagicMock()

        # Mock Pro output
        mock_agents["pro"].invoke.return_value = {
            "messages": [AIMessage(content="Pro argument")]
        }
        
        # Mock Cons output
        mock_agents["cons"].invoke.return_value = {
            "messages": [AIMessage(content="Cons argument")]
        }
        
        # Mock Arbiter output with side_effect for multiple calls
        # First call: Continue
        response_1 = {
            "messages": [AIMessage(content='Analysis... {"should_continue": true}')]
        }
        # Second call: Stop
        response_2 = {
            "messages": [AIMessage(content='Final decision... {"should_continue": false}')]
        }
        mock_agents["arbiter"].invoke.side_effect = [response_1, response_2]
        
        # Initial state
        initial_state = {
            "messages": [HumanMessage(content="Debate topic")],
            "debate_round": 0,
            "should_continue": False
        }
        
        # Run the debate workflow
        result = debate_app.invoke(initial_state)
        
        # Verify the result
        # We expect 2 rounds.
        # Round 0: pro -> cons -> arbiter (sets should_continue=True, round=1)
        # Round 1: pro -> cons -> arbiter (sets should_continue=False, round=2)
        # End.
        
        assert result["debate_round"] == 2
        assert result["should_continue"] is False
        
        # Verify call counts
        assert mock_agents["pro"].invoke.call_count == 2
        assert mock_agents["cons"].invoke.call_count == 2
        assert mock_agents["arbiter"].invoke.call_count == 2

def test_debate_logic_limit():
    """
    Test that debate stops at DEBATE_ROUND_LIMIT even if arbiter says continue.
    """
    # Import config to patch limit
    with patch('config.DEBATE_ROUND_LIMIT', 1):
        with patch.dict('agents.agents', clear=False) as mock_agents:
            
            # Replace real agents with Mocks
            mock_agents["pro"] = MagicMock()
            mock_agents["cons"] = MagicMock()
            mock_agents["arbiter"] = MagicMock()

            mock_agents["pro"].invoke.return_value = {"messages": [AIMessage(content="Pro")]}
            mock_agents["cons"].invoke.return_value = {"messages": [AIMessage(content="Cons")]}
            
            # Arbiter always says continue
            mock_agents["arbiter"].invoke.return_value = {
                "messages": [AIMessage(content='{"should_continue": true}')]
            }
            
            initial_state = {
                "messages": [HumanMessage(content="Debate topic")],
                "debate_round": 0,
                "should_continue": False
            }
            
            result = debate_app.invoke(initial_state)
            
            # Should stop after 1 round because limit is 1
            # Round 0: pro -> cons -> arbiter (sets round=1).
            # Condition: round < limit (1 < 1) is False.
            # So it stops.
            
            assert result["debate_round"] == 1
            assert mock_agents["arbiter"].invoke.call_count == 1
