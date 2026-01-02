from langchain_core.tools import tool
from typing import Optional, List, Dict, Any
import json
from compete_logging import get_logger

logger = get_logger(__name__)

# Module-level state
thought_history: List[Dict[str, Any]] = []
thought_branches: Dict[str, List[Dict[str, Any]]] = {}

def reset_thoughts():
    """Clears the thought history and branches."""
    global thought_history, thought_branches
    thought_history.clear()
    thought_branches.clear()
    logger.info("Sequential thinking state reset.")

@tool
def sequential_thinking(
    thought: str,
    thoughtNumber: int,
    totalThoughts: int,
    nextThoughtNeeded: bool,
    isRevision: Optional[bool] = False,
    revisesThought: Optional[int] = None,
    branchFromThought: Optional[int] = None,
    branchId: Optional[str] = None,
    needsMoreThoughts: Optional[bool] = None,
) -> str:
    """
    A tool for dynamic, reflective problem-solving. It allows you to think through problems step-by-step,
    revise previous thoughts, and branch out to explore different possibilities.

    Args:
        thought (str): The content of the current thought.
        thoughtNumber (int): The current thought number (1-based).
        totalThoughts (int): The estimated total number of thoughts needed.
        nextThoughtNeeded (bool): Whether another thought is needed after this one.
        isRevision (bool, optional): Whether this thought revises a previous one.
        revisesThought (int, optional): The number of the thought being revised.
        branchFromThought (int, optional): The number of the thought to branch from.
        branchId (str, optional): Identifier for the current branch.
        needsMoreThoughts (bool, optional): Explicit flag if more thoughts are needed (alternative to nextThoughtNeeded).

    Returns:
        str: A JSON string containing the current state of the thought process.
    """
    global thought_history, thought_branches

    # Normalize nextThoughtNeeded
    if needsMoreThoughts is not None:
        nextThoughtNeeded = needsMoreThoughts

    current_thought_data = {
        "thought": thought,
        "thoughtNumber": thoughtNumber,
        "totalThoughts": totalThoughts,
        "nextThoughtNeeded": nextThoughtNeeded,
        "isRevision": isRevision,
        "revisesThought": revisesThought,
        "branchFromThought": branchFromThought,
        "branchId": branchId,
    }

    # Add to history
    thought_history.append(current_thought_data)
    
    # Handle branching (simplified storage)
    if branchId:
        if branchId not in thought_branches:
            thought_branches[branchId] = []
        thought_branches[branchId].append(current_thought_data)

    # Log the thought
    logger.info(f"Sequential Thinking - Thought {thoughtNumber}/{totalThoughts}: {thought[:100]}...")

    # Construct response
    response = {
        "thought_history": thought_history,
        "current_thought": current_thought_data,
        "status": "Thinking..." if nextThoughtNeeded else "Complete"
    }

    return json.dumps(response, indent=2)
