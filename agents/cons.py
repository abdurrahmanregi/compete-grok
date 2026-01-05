"""Con Debate Agent: Pro/con debates (simplified: two grok-4-0709 instances)."""

from typing import Any

from config import DEBATE_CONS_MODEL
from . import create_agent, ALL_TOOLS
from .debate_common import DEBATE_TEAM_PROMPT

# Tool list for con agent
DEBATE_TOOLS = ALL_TOOLS

# Prepare prompt for con agent
CON_PROMPT = DEBATE_TEAM_PROMPT.replace("[Pro/Con]", "Con")


def create_cons_agent() -> Any:
    """Create the cons agent with hardcoded parameters."""
    return create_agent("cons", DEBATE_CONS_MODEL, CON_PROMPT, DEBATE_TOOLS)
