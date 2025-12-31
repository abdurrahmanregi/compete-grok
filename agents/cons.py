"""Con Debate Agent: Pro/con debates (simplified: two grok-4-0709 instances)."""

from typing import Any

from config import DEBATE_CONS_MODEL
from . import create_agent, ALL_TOOLS

# Tool list for con agent
DEBATE_TOOLS = ALL_TOOLS

# Base prompt for debate team agents (Pro and Con)
# Template with placeholder for side-specific advocacy
DEBATE_TEAM_PROMPT = """You are the [Pro/Con] advocate in a structured antitrust debate.

Present only your side forcefully but fairly, citing evidence per hierarchy.
Review previous arguments in the conversation history and directly address them.

Separate:
- Positive economic analysis
- Normative arguments (clearly labeled)"""

# Prepare prompt for con agent
CON_PROMPT = DEBATE_TEAM_PROMPT.replace("[Pro/Con]", "Con")


def create_cons_agent() -> Any:
    """Create the cons agent with hardcoded parameters."""
    return create_agent("cons", DEBATE_CONS_MODEL, CON_PROMPT, DEBATE_TOOLS)