"""Arbiter Debate Agent: Pro/con debates (simplified: two grok-4-0709 instances)."""

from typing import Any

from config import DEBATE_ARBITER_MODEL
from . import create_agent, ALL_TOOLS

# Tool list for arbiter agent
DEBATE_TOOLS = ALL_TOOLS

# System prompt for the Arbiter agent in debates
# Neutral synthesis of pro/con arguments
ARBITER_PROMPT = """You are the arbiter advocate in a structured antitrust debate.

Synthesize both sides, weigh evidence strength, provide balanced conclusion with probability ranges where possible.

Separate:
- Positive economic analysis
- Normative arguments (clearly labeled)
- Synthesize both sides, weigh evidence strength, provide balanced conclusion with probability ranges where possible."""


def create_arbiter_agent() -> Any:
    """Create the arbiter agent with hardcoded parameters."""
    return create_agent("arbiter", DEBATE_ARBITER_MODEL, ARBITER_PROMPT, DEBATE_TOOLS)