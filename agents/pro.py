"""Pro Debate Agent: Pro/con debates (simplified: two grok-4-0709 instances)."""

from typing import Any

from config import DEBATE_PRO_MODEL
from . import create_agent, ALL_TOOLS
from .debate_common import DEBATE_TEAM_PROMPT

# Tool list for pro agent
DEBATE_TOOLS = ALL_TOOLS

# Prepare prompt for pro agent
PRO_PROMPT = DEBATE_TEAM_PROMPT.replace("[Pro/Con]", "Pro")


def create_pro_agent() -> Any:
    """Create the pro agent with hardcoded parameters."""
    return create_agent("pro", DEBATE_PRO_MODEL, PRO_PROMPT, DEBATE_TOOLS)
