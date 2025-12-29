from typing import TypedDict, Annotated, Sequence, Optional, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import operator
import logging
import json
import re
from langchain_core.messages import SystemMessage

logger = logging.getLogger(__name__)

from agents import create_agent, agents
from agents.supervisor import SUPERVISOR_PROMPT
from config import SUPERVISOR_MODEL
from tools import sequential_thinking
from langchain_core.tools import tool
import config
from debate import debate_app, DebateState
from exceptions import WorkflowError, AgentError, DebateError

@tool
def route_to_econpaper(reason: str) -> str:
    """Route to EconPaper agent for paper, NBER, research queries."""
    return "econpaper"

@tool
def route_to_econquant(reason: str) -> str:
    """Route to EconQuant agent for HHI/UPP calcs, quantitative tasks."""
    return "econquant"

@tool
def route_to_explainer(reason: str) -> str:
    """Route to Explainer agent for model caveats, explanations."""
    return "explainer"

@tool
def route_to_marketdef(reason: str) -> str:
    """Route to MarketDef agent for SSNIP, market definition."""
    return "marketdef"

@tool
def route_to_docanalyzer(reason: str) -> str:
    """Route to DocAnalyzer agent for upload analysis, documents."""
    return "docanalyzer"

@tool
def route_to_caselaw(reason: str) -> str:
    """Route to CaseLaw agent for precedents, case law."""
    return "caselaw"

@tool
def route_to_debate(reason: str) -> str:
    """Route to debate subgraph for pro/con debate."""
    return "debate"

@tool
def route_to_synthesis(reason: str) -> str:
    """Route to Synthesis agent for final synthesis, integration."""
    return "synthesis"

router_tools = [
    route_to_econpaper,
    route_to_econquant,
    route_to_explainer,
    route_to_marketdef,
    route_to_docanalyzer,
    route_to_caselaw,
    route_to_debate,
    route_to_synthesis,
]

# Confidence threshold + JSON parsing for robust debate routing
def parse_supervisor_output(state):
    """Parse the Supervisor's JSON output from the last AIMessage in the state.

    Extracts routing decision data (route, confidence, justify) from the last message's
    content using regex to find JSON objects. If no JSON is found or parsing fails,
    returns default values indicating end of workflow.

    Args:
        state (dict): The current agent state containing messages.

    Returns:
        dict: Parsed route data with keys 'route', 'confidence', 'justify'.
              Defaults to {"route": "END", "confidence": 1.0, "justify": "..."} on failure.
    """
    logger.debug("Parsing supervisor output")
    try:
        if not state["messages"]:
            logger.warning("No messages in state for parsing")
            return {"route": "END", "confidence": 1.0, "justify": "No messages"}
        msg = state["messages"][-1].content
        # Use regex to find the first JSON object in the message content
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', msg, re.DOTALL)
        if not json_match:
            logger.warning("No JSON found in supervisor output")
            return {"route": "END", "confidence": 1.0, "justify": "No JSON found"}
        route_data = json.loads(json_match.group())
        # Persist route data in a system message for report/logging purposes
        next_msg = SystemMessage(content=f"Route data: {route_data}")
        state["messages"].append(next_msg)  # Temp log
        logger.debug("Successfully parsed route data: %s", route_data)
        return route_data
    except json.JSONDecodeError as e:
        logger.error("JSON parsing failed in supervisor output: %s", str(e), exc_info=True)
        return {"route": "END", "confidence": 0.5, "justify": "JSON parse fail"}
    except Exception as e:
        logger.error("Unexpected error parsing supervisor output: %s", str(e), exc_info=True)
        return {"route": "END", "confidence": 0.0, "justify": f"Unexpected parse error: {e}"}


def should_force_debate(route_data) -> bool:
    """Determine if debate mode should be forced based on routing data.

    Checks if the route is explicitly 'debate', confidence is below 0.8, or justification
    contains keywords indicating controversy or need for debate.

    Args:
        route_data (dict): Parsed route data from supervisor output.

    Returns:
        bool: True if debate should be forced, False otherwise.
    """
    conf = route_data.get("confidence", 1.0)
    justify = route_data.get("justify", "").lower()
    return (route_data.get("route") == "debate" or
            conf < 0.8 or
            any(kw in justify for kw in ["controversy", "bias", "caveat", "debate"]))

ROUTER_PROMPT = SUPERVISOR_PROMPT + f"""
You classify the query and route to the selected agents that are appropriate by calling the route_to_* tools. Do not describe routing in text; always use tool calls for routing. Prioritize routing to econpaper if selected, then verifier after econpaper if both are selected.

You can call multiple route_to_* tools in parallel if multiple agents are relevant (e.g., econpaper and econquant for a query needing both research and calculation).

After agents complete their work (you will see their output messages in subsequent invocations), you can route to more agents or provide a final synthesis by responding without tool calls (FINISH).

**LOOP PREVENTION:** If iteration_count >= {config.MAX_ITERATIONS} or if you've routed to the same agent twice in routing_history, provide final synthesis instead of routing.

**COMPLETION SIGNALS:** Look for phrases like "This completes the explanation" or "Final answer:" in agent outputs to determine when to finish.

**MULTI-ROUND DEBATE WORKFLOW:** If force_debate is True (indicated in system messages), follow this iterative workflow to ensure debates are informed by current data/modeling:
- When debate_count == 0: Route to relevant agents (e.g., econquant, econpaper) to gather initial data and analysis.
- When debate_count == 1: Route to agents again for refinement based on first debate insights.
- When debate_count == 2: Route to synthesis for final integration.
- For debate routing: After agents complete, route to debate; after debate completes, route according to the above based on updated debate_count.

Use the sequential_thinking tool for planning routes, analysis, or synthesis.

Routing triggers (call the corresponding tool):
- route_to_econpaper: paper, NBER, research
- route_to_econquant: Quant tasks (HHI, UPP, simulations, math, calculations)
- route_to_explainer: explain, caveats, model derivations
- route_to_marketdef: market definition, SSNIP
- route_to_docanalyzer: analyze document, uploads (if documents in state)
- route_to_caselaw: case law, precedent
- route_to_debate: debate, pro/con arguments
- route_to_synthesis: synthesis, final synthesis, integration

If documents are present in the state, prioritize docanalyzer.

**FINAL SYNTHESIS:** When finishing without tool calls, provide a comprehensive, complete synthesis that directly answers the original query using all information from agent outputs. Include step-by-step explanations, mathematical derivations, caveats, and references as appropriate. Do not provide partial or summary responses."""

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    routes: list[str]
    final_synthesis: str
    documents: list[str]
    iteration_count: int
    routing_history: list[str]
    sources: list[dict]
    debate_round: int
    debate_count: int
    force_debate: bool
    last_error: Optional[str]
    remediation_decision: Optional[dict]
    last_agent: str

def parse_route_tool(name: str) -> str:
    """Parse the agent name from a route tool function name.

    Extracts the agent name by removing the 'route_to_' prefix.

    Args:
        name (str): The route tool function name (e.g., 'route_to_econpaper').

    Returns:
        str: The extracted agent name (e.g., 'econpaper').

    Raises:
        ValueError: If the name does not start with 'route_to_'.
    """
    if name.startswith("route_to_"):
        return name[9:]
    raise ValueError(f"Unknown route tool: {name}")

def route_agent(state) -> str:
    """Route agent based on error state.

    If there's a last_error, route to remediation; otherwise, to supervisor.

    Args:
        state (dict): The current agent state.

    Returns:
        str: Next node name ('remediation' or 'supervisor').
    """
    if state.get("last_error"):
        return "remediation"
    else:
        return "supervisor"

def route_remediation(state) -> str:
    """Route based on remediation decision.

    Handles rephrase (back to last agent), fallback/abort (to supervisor or END).

    Args:
        state (dict): The current agent state with remediation_decision.

    Returns:
        str: Next node name or END.
    """
    decision = state.get("remediation_decision", {})
    action = decision.get("action")
    if action == "rephrase":
        return state.get("last_agent", "supervisor")
    elif action == "fallback":
        # For simplicity, go to supervisor to handle fallback
        return "supervisor"
    elif action == "abort":
        return END
    else:
        return "supervisor"

def create_workflow(selected_agents: list[str]) -> Any:
    """Create the LangGraph workflow for the CompeteGrok agent system.

    Builds a state graph with supervisor, agent nodes, debate subgraph, and remediation,
    based on selected agents. Includes routing logic, loop prevention, and conditional edges.

    Args:
        selected_agents (list[str]): List of selected agent names.

    Returns:
        Compiled LangGraph app ready for invocation.

    Raises:
        WorkflowError: If workflow creation fails.
    """
    logger.debug("Creating workflow with selected agents: %s", selected_agents)
    try:
        # Validate and filter selected agents to only include valid ones
        valid_agents = ["econpaper", "econquant", "explainer", "marketdef", "docanalyzer", "caselaw", "synthesis", "verifier"]
        AGENT_NAMES = [name for name in selected_agents if name in valid_agents]
        include_debate = any(name in selected_agents for name in ["pro", "con", "arbiter"])

        # Filter router_tools based on selected agents
        router_tools_filtered = []
        for tool in router_tools:
            route_name = parse_route_tool(tool.name) if tool.name.startswith("route_to_") else None
            if route_name and route_name in AGENT_NAMES:
                router_tools_filtered.append(tool)
            elif tool.name == "route_to_debate" and include_debate:
                router_tools_filtered.append(tool)
            elif tool.name == "route_to_synthesis" and "synthesis" in AGENT_NAMES:
                router_tools_filtered.append(tool)

        # Create supervisor with filtered tools
        supervisor_router_filtered = create_agent(
            "supervisor_router",
            SUPERVISOR_MODEL,
            ROUTER_PROMPT,
            tools=router_tools_filtered + [sequential_thinking]
        )

        agent_map = {name: name for name in AGENT_NAMES}
        if include_debate:
            agent_map["debate"] = "debate"

        def route_supervisor(state):
            routes = state.get("routes", [])
            iteration_count = state.get("iteration_count", 0)
            routing_history = state.get("routing_history", [])

            if routes:
                # Check if routing to same agent repeatedly
                if any(routing_history.count(route) > 1 for route in routes):
                    return END
                return routes[0]  # Single route for conditional; extend to parallel if needed

            # If no routes, route to synthesis for final synthesis if synthesis is selected, else end
            if "synthesis" in AGENT_NAMES:
                return "synthesis"
            else:
                return END

        def create_agent_node(agent_name: str):
            """Factory function to create a node function for the given agent.

            Args:
                agent_name (str): Name of the agent.

            Returns:
                function: Node function that invokes the agent and updates state.
            """
            def node(state: AgentState) -> dict:
                logger.debug("Entering agent node: %s", agent_name)
                try:
                    # For synthesis, filter messages to reduce context size
                    messages_to_use = state["messages"]
                    if agent_name == "synthesis":
                        # Filter to key agent outputs: AIMessages without tool_calls (final responses) that are not routing messages
                        filtered_messages = []
                        for msg in state["messages"]:
                            if isinstance(msg, AIMessage):
                                content_lower = msg.content.lower()
                                # Exclude supervisor routing messages and messages with tool_calls
                                if not any(word in content_lower for word in ["route", "current state", "force debate"]) and not hasattr(msg, "tool_calls") or not msg.tool_calls:
                                    filtered_messages.append(msg)
                            elif isinstance(msg, HumanMessage):
                                # Include the original query
                                filtered_messages.append(msg)
                        messages_to_use = filtered_messages

                    result = agents[agent_name].invoke({"messages": messages_to_use})
                    logger.info("Node %s complete", agent_name)
                    final_synthesis = ""
                    if agent_name == "synthesis":
                        for msg in reversed(result["messages"]):
                            if isinstance(msg, AIMessage) and msg.content.strip():
                                final_synthesis = msg.content
                                break

                    # Collect sources from tool outputs
                    new_sources = []
                    existing_urls = {s.get("url") for s in state.get("sources", [])}
                    for msg in result["messages"]:
                        if hasattr(msg, "content") and isinstance(msg.content, dict) and "sources" in msg.content:
                            for source in msg.content["sources"]:
                                if source.get("url") and source["url"] not in existing_urls:
                                    new_sources.append(source)
                                    existing_urls.add(source["url"])

                    return {
                        "messages": result["messages"],
                        "iteration_count": state.get("iteration_count", 0) + 1,
                        "routing_history": state.get("routing_history", []) + [agent_name],
                        "final_synthesis": final_synthesis,
                        "sources": state.get("sources", []) + new_sources,
                        "last_error": None,
                        "last_agent": agent_name
                    }
                except Exception as e:
                    logger.error("Error in %s: %s", agent_name, str(e), exc_info=True)
                    error_msg = f"Error in {agent_name}: {e}. Reflect: retry or caveats."
                    final_synthesis = error_msg if agent_name == "synthesis" else state.get("final_synthesis", "")
                    return {
                        "messages": [SystemMessage(content=error_msg)],
                        "iteration_count": state.get("iteration_count", 0) + 1,
                        "routing_history": state.get("routing_history", []) + [agent_name],
                        "final_synthesis": final_synthesis,
                        "sources": state.get("sources", []),
                        "last_error": error_msg,
                        "last_agent": agent_name
                    }
            return node

        agent_nodes = {name: create_agent_node(name) for name in AGENT_NAMES}

        def supervisor_node(state: AgentState) -> dict:
            """Supervisor node that determines next routing based on agent selection and history.

            Parses selected agents, applies deterministic routing logic, prevents loops,
            and updates state with routes and messages.

            Args:
                state (AgentState): Current agent state.

            Returns:
                dict: Updated state with routes, messages, etc.
            """
            logger.debug("Entering supervisor node")
            try:
                # Extract selected_agents from the first HumanMessage
                selected_agents = []
                for msg in state["messages"]:
                    if isinstance(msg, HumanMessage):
                        content = msg.content
                        if "Selected agents:" in content:
                            start = content.find("Selected agents:") + len("Selected agents:")
                            end = content.find("\n\nForce debate:")
                            if end == -1:
                                end = len(content)
                            agents_str = content[start:end].strip()
                            selected_agents = json.loads(agents_str)
                            break

                # Deterministic routing logic based on selected_agents and routing_history
                routing_history = state.get("routing_history", [])
                agents_to_route = [a for a in selected_agents if a not in ["synthesis", "verifier", "pro", "con", "arbiter"] and a not in routing_history]
                if agents_to_route:
                    routes = [agents_to_route[0]]
                elif "verifier" in selected_agents and "verifier" not in routing_history and ("econpaper" in routing_history or "caselaw" in routing_history):
                    routes = ["verifier"]
                elif state.get("force_debate", False) and any(name in selected_agents for name in ["pro", "con", "arbiter"]):
                    routes = ["debate"]
                else:
                    routes = []

                # Update routing_history
                routing_history = routing_history + routes

                # Add routing message
                routing_msg = SystemMessage(content=f"Deterministic routes: {routes}")

                # Loop prevention logic
                current_iteration = state.get("iteration_count", 0) + 1

                # Check for loops
                if current_iteration >= config.MAX_CURRENT_ITERATION:  # Hard limit
                    routes = []
                elif len([h for h in routing_history if h in routes]) > config.HISTORY_THRESHOLD:  # Same agent twice
                    routes = []

                # Set synthesis if no routes determined
                final_synthesis = ""
                if not routes:
                    final_synthesis = "Routing complete, proceeding to synthesis."

                logger.info("Node supervisor complete, routes: %s, iteration: %d", routes, current_iteration)
                return {
                    "messages": operator.add(state["messages"], [routing_msg]),
                    "routes": routes,
                    "iteration_count": state.get("iteration_count", 0),
                    "routing_history": routing_history,
                    "final_synthesis": final_synthesis,
                    "sources": state.get("sources", [])
                }
            except json.JSONDecodeError as e:
                logger.error("JSON parsing error in supervisor: %s", str(e), exc_info=True)
                return {"messages": [SystemMessage(content=f"Error parsing agents in supervisor: {e}. Reflect: retry or caveats.")]}
            except Exception as e:
                logger.error("Unexpected error in supervisor: %s", str(e), exc_info=True)
                return {"messages": [SystemMessage(content=f"Error in supervisor: {e}. Reflect: retry or caveats.")]}

        # Main workflow
        workflow = StateGraph(AgentState)
        workflow.add_node("supervisor", supervisor_node)
        for name in AGENT_NAMES:
            workflow.add_node(name, agent_nodes[name])
        if include_debate:
            workflow.add_node("debate", debate_node)
        workflow.add_node("remediation", remediation_node)

        workflow.set_entry_point("supervisor")
        workflow.add_conditional_edges(
            "supervisor",
            route_supervisor,
            {**agent_map, "__end__": END, "END": END, "supervisor": "supervisor"}
        )

        # Conditional edges from agents: success -> supervisor, failure -> remediation
        for name in AGENT_NAMES:
            if name != "synthesis":
                workflow.add_conditional_edges(name, route_agent, {"supervisor": "supervisor", "remediation": "remediation"})

        if "synthesis" in AGENT_NAMES:
            workflow.add_edge("synthesis", END)
        if include_debate:
            workflow.add_edge("debate", "supervisor")

        # From remediation, conditional based on decision
        workflow.add_conditional_edges("remediation", route_remediation, {**agent_map, "__end__": END, "END": END, "supervisor": "supervisor"})

        app = workflow.compile()
        logger.info("Workflow created successfully")
        return app
    except Exception as e:
        logger.error("Failed to create workflow: %s", str(e), exc_info=True)
        raise WorkflowError(f"Workflow creation failed: {e}") from e


def debate_node(state: AgentState) -> dict:
    """Invoke the debate subgraph and update state with debate results."""
    logger.debug("Entering debate node")
    try:
        result = debate_app.invoke(state)
        logger.info("Node debate complete")
        return {
            "messages": operator.add(state["messages"], result["messages"]),
            "debate_count": state.get("debate_count", 0) + 1,
            "sources": state.get("sources", [])
        }
    except DebateError as e:
        logger.error("Debate-specific error: %s", str(e), exc_info=True)
        return {"messages": [SystemMessage(content=f"Debate error: {e}. Reflect: retry or caveats.")], "last_error": str(e)}
    except Exception as e:
        logger.error("Unexpected error in debate: %s", str(e), exc_info=True)
        return {"messages": [SystemMessage(content=f"Error in debate: {e}. Reflect: retry or caveats.")], "last_error": str(e)}

def remediation_node(state: AgentState) -> dict:
    """Handle remediation by invoking remediation agent and executing decision."""
    logger.debug("Entering remediation node")
    if not state.get("last_error"):
        logger.debug("No last error, skipping remediation")
        return state
    try:
        # Create message for remediation agent
        error_msg = state["last_error"]
        task_instructions = "Process the error and decide on remediation action."
        tool_name = "unknown"  # Could be improved to extract from error
        human_msg = HumanMessage(content=f"Tool '{tool_name}' failed with error: '{error_msg}'. Task: {task_instructions}")
        result = agents["remediation"].invoke({"messages": [human_msg]})
        # Parse JSON decision
        content = result["messages"][-1].content
        decision = json.loads(content)
        logger.info("Remediation decision: %s", decision)
        # Handle decision
        action = decision.get("action")
        if action == "rephrase":
            new_query = decision.get("new_args", {}).get("query", "Retry with rephrased query")
            # Add system message to instruct retry
            retry_msg = SystemMessage(content=f"Remediation: Rephrase and retry. New query: {new_query}")
            return {
                "messages": [retry_msg],
                "remediation_decision": decision
            }
        elif action == "fallback":
            new_tool = decision.get("new_tool", "supervisor")
            fallback_msg = SystemMessage(content=f"Remediation: Fallback to {new_tool}")
            return {
                "messages": [fallback_msg],
                "remediation_decision": decision
            }
        elif action == "abort":
            abort_msg = SystemMessage(content="Remediation: Abort task")
            return {
                "messages": [abort_msg],
                "remediation_decision": decision,
                "final_synthesis": "Task aborted due to unrecoverable error."
            }
        else:
            logger.warning("Unknown remediation action: %s", action)
            return {
                "messages": [SystemMessage(content="Remediation: Unknown action")],
                "remediation_decision": decision
            }
    except json.JSONDecodeError as e:
        logger.error("JSON parsing error in remediation: %s", str(e), exc_info=True)
        return {"messages": [SystemMessage(content=f"Remediation parsing error: {e}")], "last_error": str(e)}
    except Exception as e:
        logger.error("Unexpected error in remediation: %s", str(e), exc_info=True)
        return {"messages": [SystemMessage(content=f"Error in remediation: {e}")], "last_error": str(e)}
