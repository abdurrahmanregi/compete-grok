# Debate logic separated for modularity

from typing import TypedDict, Sequence, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, SystemMessage
import logging

from agents import agents
import config
from exceptions import DebateError

logger = logging.getLogger(__name__)

class DebateState(TypedDict):
    messages: Sequence[BaseMessage]
    debate_round: int

def pro_node(state: DebateState) -> dict:
    """Invoke the pro debate agent and return updated messages."""
    logger.debug("Entering pro_node")
    try:
        result = agents["pro"].invoke({"messages": state["messages"]})
        logger.info("Pro agent completed successfully")
        return {"messages": result["messages"]}
    except Exception as e:
        logger.error("Error in pro_node: %s", str(e), exc_info=True)
        error_msg = f"Error in pro debate agent: {e}. Reflect: retry or caveats."
        return {"messages": [SystemMessage(content=error_msg)]}

def cons_node(state: DebateState) -> dict:
    """Invoke the cons debate agent and return updated messages."""
    logger.debug("Entering cons_node")
    try:
        result = agents["cons"].invoke({"messages": state["messages"]})
        logger.info("Cons agent completed successfully")
        return {"messages": result["messages"]}
    except Exception as e:
        logger.error("Error in cons_node: %s", str(e), exc_info=True)
        error_msg = f"Error in cons debate agent: {e}. Reflect: retry or caveats."
        return {"messages": [SystemMessage(content=error_msg)]}

def arbiter_node(state: DebateState) -> dict:
    """Invoke the arbiter debate agent and increment debate round."""
    logger.debug("Entering arbiter_node")
    try:
        result = agents["arbiter"].invoke({"messages": state["messages"]})
        logger.info("Arbiter agent completed successfully")
        return {
            "messages": result["messages"],
            "debate_round": state.get("debate_round", 0) + 1
        }
    except Exception as e:
        logger.error("Error in arbiter_node: %s", str(e), exc_info=True)
        error_msg = f"Error in arbiter debate agent: {e}. Reflect: retry or caveats."
        return {
            "messages": [SystemMessage(content=error_msg)],
            "debate_round": state.get("debate_round", 0) + 1  # Still increment to avoid loops
        }

debate_workflow = StateGraph(DebateState)
debate_workflow.add_node("pro", pro_node)
debate_workflow.add_node("cons", cons_node)
debate_workflow.add_node("arbiter", arbiter_node)
debate_workflow.set_entry_point("pro")
debate_workflow.add_edge("pro", "cons")
debate_workflow.add_edge("cons", "arbiter")
debate_workflow.add_conditional_edges(
    "arbiter",
    lambda state: "pro" if state.get("debate_round", 0) < config.DEBATE_ROUND_LIMIT else END,
    {"pro": "pro", "__end__": END}
)
debate_app = debate_workflow.compile()