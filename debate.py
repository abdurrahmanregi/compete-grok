# Debate logic separated for modularity

from typing import TypedDict, Sequence, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage

from agents.agents import agents
import config

class DebateState(TypedDict):
    messages: Sequence[BaseMessage]
    debate_round: int

def pro_node(state: DebateState) -> dict:
    """Invoke the pro debate agent and return updated messages."""
    result = agents["pro"].invoke({"messages": state["messages"]})
    return {"messages": result["messages"]}

def con_node(state: DebateState) -> dict:
    """Invoke the con debate agent and return updated messages."""
    result = agents["con"].invoke({"messages": state["messages"]})
    return {"messages": result["messages"]}

def arbiter_node(state: DebateState) -> dict:
    """Invoke the arbiter debate agent and increment debate round."""
    result = agents["arbiter"].invoke({"messages": state["messages"]})
    return {
        "messages": result["messages"],
        "debate_round": state.get("debate_round", 0) + 1
    }

debate_workflow = StateGraph(DebateState)
debate_workflow.add_node("pro", pro_node)
debate_workflow.add_node("con", con_node)
debate_workflow.add_node("arbiter", arbiter_node)
debate_workflow.set_entry_point("pro")
debate_workflow.add_edge("pro", "con")
debate_workflow.add_edge("con", "arbiter")
debate_workflow.add_conditional_edges(
    "arbiter",
    lambda state: "pro" if state.get("debate_round", 0) < config.DEBATE_ROUND_LIMIT else END,
    {"pro": "pro", "__end__": END}
)
debate_app = debate_workflow.compile()