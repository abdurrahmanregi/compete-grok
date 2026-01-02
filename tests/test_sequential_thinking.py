import pytest
import json
from tools.sequential_thinking import sequential_thinking, reset_thoughts, thought_history, thought_branches

@pytest.fixture(autouse=True)
def setup_teardown():
    reset_thoughts()
    yield
    reset_thoughts()

def test_basic_thought_recording():
    result_json = sequential_thinking.invoke({
        "thought": "Initial thought",
        "thoughtNumber": 1,
        "totalThoughts": 3,
        "nextThoughtNeeded": True
    })
    result = json.loads(result_json)
    
    assert result["current_thought"]["thought"] == "Initial thought"
    assert result["current_thought"]["thoughtNumber"] == 1
    assert len(result["thought_history"]) == 1
    assert result["status"] == "Thinking..."

def test_state_persistence():
    sequential_thinking.invoke({
        "thought": "First thought",
        "thoughtNumber": 1,
        "totalThoughts": 2,
        "nextThoughtNeeded": True
    })
    
    result_json = sequential_thinking.invoke({
        "thought": "Second thought",
        "thoughtNumber": 2,
        "totalThoughts": 2,
        "nextThoughtNeeded": False
    })
    result = json.loads(result_json)
    
    assert len(result["thought_history"]) == 2
    assert result["thought_history"][0]["thought"] == "First thought"
    assert result["thought_history"][1]["thought"] == "Second thought"
    assert result["status"] == "Complete"

def test_branching_logic():
    sequential_thinking.invoke({
        "thought": "Main branch thought",
        "thoughtNumber": 1,
        "totalThoughts": 3,
        "nextThoughtNeeded": True
    })
    
    result_json = sequential_thinking.invoke({
        "thought": "Alternative path",
        "thoughtNumber": 2,
        "totalThoughts": 3,
        "nextThoughtNeeded": True,
        "branchFromThought": 1,
        "branchId": "alt-1"
    })
    result = json.loads(result_json)
    
    assert result["current_thought"]["branchId"] == "alt-1"
    assert result["current_thought"]["branchFromThought"] == 1
    
    # Check internal state directly
    assert "alt-1" in thought_branches
    assert len(thought_branches["alt-1"]) == 1
    assert thought_branches["alt-1"][0]["thought"] == "Alternative path"

def test_revision_logic():
    sequential_thinking.invoke({
        "thought": "Original thought",
        "thoughtNumber": 1,
        "totalThoughts": 3,
        "nextThoughtNeeded": True
    })
    
    result_json = sequential_thinking.invoke({
        "thought": "Revised thought",
        "thoughtNumber": 2,
        "totalThoughts": 3,
        "nextThoughtNeeded": True,
        "isRevision": True,
        "revisesThought": 1
    })
    result = json.loads(result_json)
    
    assert result["current_thought"]["isRevision"] is True
    assert result["current_thought"]["revisesThought"] == 1
    assert result["thought_history"][1]["thought"] == "Revised thought"

def test_reset_thoughts():
    sequential_thinking.invoke({
        "thought": "Some thought",
        "thoughtNumber": 1,
        "totalThoughts": 1,
        "nextThoughtNeeded": False
    })
    
    assert len(thought_history) == 1
    
    reset_thoughts()
    
    assert len(thought_history) == 0
