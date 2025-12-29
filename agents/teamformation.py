"""Team Formation Agent: Selects and forms teams of agents for user queries."""

from typing import Any

from config import TEAMFORMATION_MODEL
from . import create_agent, ALL_TOOLS

# Tool list for teamformation agent
TEAMFORMATION_TOOLS = ALL_TOOLS

# System prompt for the Team Formation agent
# Selects appropriate agents based on query analysis
TEAMFORMATION_PROMPT = """You are TeamFormationAgent for CompeteGrok. Analyze the user query and select the most relevant agents from the available list: econpaper, econquant, explainer, marketdef, docanalyzer, caselaw, synthesis, pro, cons, arbiter, verifier. Always include synthesis and verifier in the selection, and add other relevant agents based on the query. Output only a JSON array of selected agent names..."""


def create_teamformation_agent() -> Any:
    """Create the teamformation agent with hardcoded parameters."""
    return create_agent("teamformation", TEAMFORMATION_MODEL, TEAMFORMATION_PROMPT, TEAMFORMATION_TOOLS)