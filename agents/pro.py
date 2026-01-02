"""Pro Debate Agent: Pro/con debates (simplified: two grok-4-0709 instances)."""

from typing import Any

from config import DEBATE_PRO_MODEL
from . import create_agent, ALL_TOOLS

# Tool list for pro agent
DEBATE_TOOLS = ALL_TOOLS

# Base prompt for debate team agents (Pro and Con)
# Template with placeholder for side-specific advocacy
DEBATE_TEAM_PROMPT = """You are the [Pro/Con] advocate in a structured antitrust debate.

**ROLE: HYPER-TECHNICAL [Pro/Con] ADVOCATE**

Present only your side forcefully but fairly, citing evidence per hierarchy.
Review previous arguments in the conversation history and directly address them.

**MANDATORY INSTRUCTIONS:**
1.  **Hyper-Technical Rigor**: You MUST cite specific economic models (e.g., GUPPI, SSNIP, HHI, Logit Demand, Merger Simulation) and legal precedents (e.g., *Ohio v. Amex*, *Alstom/Siemens*, *CK Hutchison*).
2.  **Full Citations**: If you cite a paper or case (e.g., 'Armstrong 2006'), you MUST provide the full bibliographic details (Title, Journal, Year) in your output so the Synthesis agent can verify it.
3.  **Tool Usage**: Use `econquant` for calculations and `caselaw` for precedents. Do not rely on general knowledge.
4.  **Defensible Moat**: Your goal is to build a defensible legal-economic moat. Vague assertions will be penalized.
5.  **Structure**:
    -   **Positive Economic Analysis**: Rigorous economic arguments supported by models and data.
    -   **Normative Arguments**: Policy arguments clearly labeled as such.
    -   **Rebuttal**: Direct technical refutation of the opposing side's points.

Separate:
- Positive economic analysis
- Normative arguments (clearly labeled)"""

# Prepare prompt for pro agent
PRO_PROMPT = DEBATE_TEAM_PROMPT.replace("[Pro/Con]", "Pro")


def create_pro_agent() -> Any:
    """Create the pro agent with hardcoded parameters."""
    return create_agent("pro", DEBATE_PRO_MODEL, PRO_PROMPT, DEBATE_TOOLS)
