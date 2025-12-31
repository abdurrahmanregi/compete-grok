"""Pro Debate Agent: Pro/con debates (simplified: two grok-4-0709 instances)."""

from typing import Any

from config import DEBATE_PRO_MODEL
from . import create_agent, ALL_TOOLS

# Tool list for pro agent
DEBATE_TOOLS = ALL_TOOLS

# Base prompt for debate team agents (Pro and Con)
# Template with placeholder for side-specific advocacy
DEBATE_TEAM_PROMPT = """You are the [Pro/Con] advocate in a structured antitrust debate.

Present only your side forcefully but fairly, citing evidence per hierarchy.
Review previous arguments in the conversation history and directly address them.

Separate:
- Positive economic analysis
- Normative arguments (clearly labeled)"""

# Prepare prompt for pro agent
PRO_PROMPT = DEBATE_TEAM_PROMPT.replace("[Pro/Con]", "Pro")


def create_pro_agent() -> Any:
    """Create the pro agent with hardcoded parameters."""
    return create_agent("pro", DEBATE_PRO_MODEL, PRO_PROMPT, DEBATE_TOOLS)