"""Market Definition Expert Agent: Market definition (SSNIP, etc.)."""

from typing import Any

from config import MARKETDEF_MODEL
from . import create_agent, ALL_TOOLS

# Tool list for marketdef agent
MARKETDEF_TOOLS = ALL_TOOLS

# System prompt for the Market Definition Expert agent
# Defines markets using SSNIP tests and related methods
MARKETDEF_PROMPT = """You are a Market Definition Expert.

Primary tool: Hypothetical Monopolist Test (SSNIP) under 2023 US HMG and EU guidelines.

Mandatory steps:
1. Discuss candidate markets
2. Evaluate evidence types: critical loss analysis, natural experiments, diversion ratios, pricing correlations, switching data
3. Consider cellophane fallacy and existing market power
4. Address zero-price and multi-sided platform issues separately
5. Conclude on narrowest plausible market under each jurisdiction"""


def create_marketdef_agent() -> Any:
    """Create the marketdef agent with hardcoded parameters."""
    return create_agent("marketdef", MARKETDEF_MODEL, MARKETDEF_PROMPT, MARKETDEF_TOOLS)