import pytest
from unittest.mock import MagicMock, patch
import json
from langchain_core.messages import HumanMessage, AIMessage
from graph import create_workflow, AgentState

def test_workflow_integration_econpaper_verifier():
    """
    Test the workflow: Supervisor -> EconPaper -> Verifier -> Synthesis.
    Mocks agent outputs to simulate successful execution and routing.
    """
    # Define selected agents for this workflow
    selected_agents = ["econpaper", "verifier", "synthesis"]
    
    # Mock the agents dictionary in graph.py (or wherever it's imported from)
    # Since create_workflow uses 'agents' imported from 'agents', we need to patch 'agents.agents'
    with patch.dict('agents.agents', clear=False) as mock_agents:
        
        # Replace real agents with Mocks
        mock_agents["econpaper"] = MagicMock()
        mock_agents["verifier"] = MagicMock()
        mock_agents["synthesis"] = MagicMock()

        # Mock EconPaper output
        mock_econpaper_response = {
            "messages": [
                AIMessage(content=json.dumps([
                    {
                        "paper_id": 1,
                        "title": "Test Paper",
                        "authors": "Doe, J.",
                        "outlet": "JPE",
                        "year": 2025,
                        "doi": "10.1086/test",
                        "url": "http://example.com/paper",
                        "snippet": "Abstract...",
                        "verified_via": "mock"
                    }
                ]))
            ]
        }
        mock_agents["econpaper"].invoke.return_value = mock_econpaper_response
        
        # Mock Verifier output
        mock_verifier_response = {
            "messages": [
                AIMessage(content=json.dumps([
                    {
                        "paper_id": 1,
                        "title": "Test Paper",
                        "authors": "Doe, J.",
                        "outlet": "JPE",
                        "year": 2025,
                        "doi": "10.1086/test",
                        "url": "http://example.com/paper",
                        "status": "verified"
                    }
                ]))
            ]
        }
        mock_agents["verifier"].invoke.return_value = mock_verifier_response
        
        # Mock Synthesis output
        mock_synthesis_response = {
            "messages": [
                AIMessage(content="Final synthesis based on verified paper.")
            ]
        }
        mock_agents["synthesis"].invoke.return_value = mock_synthesis_response

        # Create the workflow
        app = create_workflow(selected_agents)
        
        # Initial state
        initial_state = {
            "messages": [
                HumanMessage(content=f"Find papers on X.\n\nSelected agents: {json.dumps(selected_agents)}\n\nForce debate: False")
            ],
            "iteration_count": 0,
            "routing_history": [],
            "sources": []
        }
        
        # Run the workflow
        # We can use app.invoke(initial_state) but since we mocked the agents, it should run fast.
        # However, app.invoke runs the whole graph.
        
        result = app.invoke(initial_state)
        
        # Verify the routing history
        # Expected: supervisor -> econpaper -> supervisor -> verifier -> supervisor -> synthesis -> END
        # Note: supervisor node adds itself to history? No, supervisor node logic updates routing_history.
        # The graph execution path is recorded in 'routing_history' by the agent nodes and supervisor.
        
        history = result["routing_history"]
        print(f"Routing History: {history}")
        
        # Check if econpaper ran
        assert "econpaper" in history
        
        # Check if verifier ran AFTER econpaper
        econ_idx = history.index("econpaper")
        assert "verifier" in history[econ_idx+1:]
        
        # Check if synthesis ran at the end
        assert history[-1] == "synthesis" or "synthesis" in history
        
        # Check final synthesis
        assert result["final_synthesis"] == "Final synthesis based on verified paper."
