# Debate logic separated for modularity

from typing import TypedDict, Sequence, Any, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, SystemMessage, AIMessage
import logging
import json
import re

from agents import agents
import config
from exceptions import DebateError

logger = logging.getLogger(__name__)

class DebateState(TypedDict):
    messages: Sequence[BaseMessage]
    debate_round: int
    should_continue: bool

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
        
        # Parse should_continue and feedback from arbiter output
        should_continue = False
        feedback = None
        last_msg = result["messages"][-1]
        
        if isinstance(last_msg, AIMessage):
            content = last_msg.content
            # Look for JSON containing should_continue
            # Use a more permissive regex to capture the full JSON object including feedback
            json_match = re.search(r'\{.*"should_continue".*\}', content, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group())
                    should_continue = data.get("should_continue", False)
                    feedback = data.get("feedback")
                except json.JSONDecodeError:
                    logger.warning("Failed to parse JSON from arbiter output")
        
        # Inject feedback as a SystemMessage if continuing
        messages = result["messages"]
        if should_continue and feedback:
            logger.info(f"Injecting arbiter feedback: {feedback}")
            messages.append(SystemMessage(content=f"Moderator Feedback for next round: {feedback}"))

        return {
            "messages": messages,
            "debate_round": state.get("debate_round", 0) + 1,
            "should_continue": should_continue
        }
    except Exception as e:
        logger.error("Error in arbiter_node: %s", str(e), exc_info=True)
        error_msg = f"Error in arbiter debate agent: {e}. Reflect: retry or caveats."
        return {
            "messages": [SystemMessage(content=error_msg)],
            "debate_round": state.get("debate_round", 0) + 1,  # Still increment to avoid loops
            "should_continue": False
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
    lambda state: "pro" if state.get("should_continue", False) and state.get("debate_round", 0) < config.DEBATE_ROUND_LIMIT else END,
    {"pro": "pro", "__end__": END}
)
debate_app = debate_workflow.compile()