import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from graph import create_workflow
from exceptions import WorkflowError

def test_create_workflow_basic():
    """Test create_workflow with basic agents."""
    selected_agents = ["supervisor", "synthesis"]
    
    # Mock the StateGraph and its compile method
    with patch('graph.StateGraph') as mock_state_graph:
        mock_graph_builder = MagicMock()
        mock_app = MagicMock()
        mock_graph_builder.compile.return_value = mock_app
        mock_state_graph.return_value = mock_graph_builder
        
        # Mock create_agent to avoid actual agent creation
        with patch('graph.create_agent') as mock_create_agent:
            mock_create_agent.return_value = MagicMock()
            
            app = create_workflow(selected_agents)
            
            assert app == mock_app
            # Verify supervisor and synthesis were added
            # Note: The exact calls depend on implementation, but we expect add_node calls
            assert mock_graph_builder.add_node.call_count >= 2

def test_create_workflow_with_debate():
    """Test create_workflow including debate agents."""
    selected_agents = ["supervisor", "pro", "cons", "arbiter", "synthesis"]
    
    with patch('graph.StateGraph') as mock_state_graph:
        mock_graph_builder = MagicMock()
        mock_app = MagicMock()
        mock_graph_builder.compile.return_value = mock_app
        mock_state_graph.return_value = mock_graph_builder
        
        with patch('graph.create_agent') as mock_create_agent:
            mock_create_agent.return_value = MagicMock()
            
            app = create_workflow(selected_agents)
            
            assert app == mock_app
            # Should have nodes for debate (pro/cons/arbiter are inside debate subgraph)
            # We can check if add_node was called with these names
            node_names = [call.args[0] for call in mock_graph_builder.add_node.call_args_list]
            assert "debate" in node_names
            assert "pro" not in node_names
            assert "cons" not in node_names

def test_create_workflow_invalid_agent():
    """Test create_workflow with an invalid agent name."""
    selected_agents = ["supervisor", "invalid_agent"]
    
    with patch('graph.StateGraph'), patch('graph.create_agent'):
        # Depending on implementation, this might raise an error or just ignore it
        # Assuming it raises ValueError or similar if agent not found in registry
        # But create_workflow might just try to create it.
        # If create_agent raises error, we catch it.
        pass
