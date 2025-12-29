import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from unittest.mock import patch, MagicMock
from graph import parse_supervisor_output, should_force_debate, parse_route_tool, route_agent, route_remediation

def test_parse_supervisor_output_valid_json():
    """Test parsing valid JSON from supervisor output."""
    state = {"messages": [MagicMock(content='{"route": "econpaper", "confidence": 0.9, "justify": "test"}')]}
    result = parse_supervisor_output(state)
    assert result["route"] == "econpaper"
    assert result["confidence"] == 0.9

def test_parse_supervisor_output_no_json():
    """Test parsing when no JSON found."""
    state = {"messages": [MagicMock(content="No JSON here")]}
    result = parse_supervisor_output(state)
    assert result["route"] == "END"

def test_should_force_debate_high_confidence():
    """Test debate forcing with high confidence."""
    route_data = {"route": "econpaper", "confidence": 0.95, "justify": "clear"}
    assert not should_force_debate(route_data)

def test_should_force_debate_low_confidence():
    """Test debate forcing with low confidence."""
    route_data = {"route": "econpaper", "confidence": 0.7, "justify": "unclear"}
    assert should_force_debate(route_data)

def test_should_force_debate_explicit():
    """Test debate forcing when route is debate."""
    route_data = {"route": "debate", "confidence": 1.0, "justify": "test"}
    assert should_force_debate(route_data)

def test_parse_route_tool_valid():
    """Test parsing valid route tool name."""
    assert parse_route_tool("route_to_econpaper") == "econpaper"

def test_parse_route_tool_invalid():
    """Test parsing invalid route tool name."""
    with pytest.raises(ValueError):
        parse_route_tool("invalid_tool")

def test_route_agent_with_error():
    """Test route_agent with last_error."""
    state = {"last_error": "some error"}
    result = route_agent(state)
    assert result == "remediation"

def test_route_agent_no_error():
    """Test route_agent without last_error."""
    state = {}
    result = route_agent(state)
    assert result == "supervisor"

def test_route_remediation_rephrase():
    """Test route_remediation with rephrase action."""
    state = {"remediation_decision": {"action": "rephrase"}, "last_agent": "econpaper"}
    result = route_remediation(state)
    assert result == "econpaper"

def test_route_remediation_fallback():
    """Test route_remediation with fallback action."""
    state = {"remediation_decision": {"action": "fallback"}}
    result = route_remediation(state)
    assert result == "supervisor"

def test_route_remediation_abort():
    """Test route_remediation with abort action."""
    state = {"remediation_decision": {"action": "abort"}}
    result = route_remediation(state)
    from langgraph.graph import END
    assert result == END

def test_create_workflow_basic():
    """Test create_workflow with basic agents."""
    selected_agents = ["supervisor", "synthesis"]
    with patch('graph.create_agent') as mock_create_agent, \
         patch('graph.StateGraph') as mock_state_graph:
        mock_agent = MagicMock()
        mock_create_agent.return_value = mock_agent
        mock_app = MagicMock()
        mock_graph = MagicMock()
        mock_graph.compile.return_value = mock_app
        mock_state_graph.return_value = mock_graph

        result = create_workflow(selected_agents)
        assert result == mock_app