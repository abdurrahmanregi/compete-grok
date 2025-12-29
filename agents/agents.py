from typing import Any, List, Optional

from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.prebuilt import create_react_agent

from config import *
from tools import *
from .prompts import *

class MockChatModel(ChatOpenAI):
    """Mock ChatOpenAI model for testing when API key is not available.

    Generates fixed mock responses for development and testing purposes.
    """
    def __init__(self, model_name: str, **kwargs):
        """Initialize the mock model with dummy API settings.

        Args:
            model_name (str): Name of the model to mock.
            **kwargs: Additional arguments passed to parent.
        """
        kwargs["model"] = model_name
        kwargs["api_key"] = "dummy"
        kwargs["base_url"] = "https://api.x.ai/v1"
        super().__init__(**kwargs)
        self.model_name = model_name

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate a mock response for testing purposes.

        Returns a fixed mock message simulating agent output.

        Args:
            messages: Input messages (ignored).
            stop: Stop sequences (ignored).
            run_manager: Run manager (ignored).
            **kwargs: Additional arguments (ignored).

        Returns:
            ChatResult: Mock chat result with fixed content.
        """
        last_message = messages[-1].content if messages else ""
        mock_content = rf"""Hypothesis: Analyzed '{last_message}' → {self.model_name} task (e.g., HHI calc, SSNIP sim).

Used sequential_thinking. Tools: run_code_py/r for quants, tavily_search for papers.

Output: \[ HHI = \sum_i s_i^2 \]

Reflection: Hypothesis tested; caveats (2025 data, IIA fails); robust via mocks."""
        generation = ChatGeneration(message=AIMessage(content=mock_content))
        return ChatResult(generations=[generation])

def create_agent(name: str, model: str, system_prompt: str, tools: list) -> Any:
    """Create a LangGraph react agent with specified model, prompt, and tools.

    Uses real ChatOpenAI if API key is available, otherwise MockChatModel.

    Args:
        name (str): Agent name for sampling params.
        model (str): Model name.
        system_prompt (str): System prompt for the agent.
        tools (list): List of tools for the agent.

    Returns:
        LangGraph agent instance.
    """
    print(f"Creating agent '{name}' with model '{model}' and system_prompt length {len(system_prompt)}")
    sampling = SAMPLING_PARAMS.get(name, SAMPLING_PARAMS["default"])
    if not XAI_API_KEY:
        llm = MockChatModel(model_name=model, **sampling)
    else:
        llm = ChatOpenAI(
            model=model,
            api_key=XAI_API_KEY,
            base_url="https://api.x.ai/v1",
            **sampling
        )
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ])
    return create_react_agent(llm, tools, prompt=prompt)

# Tool bindings
ALL_TOOLS = [
    run_code_py,
    run_code_r,
    tavily_search,
    tavily_extract,
    linkup_search,
    linkup_fetch,
    sequential_thinking,
    convert_pdf_url,
    convert_pdf_file,
    read_text_file,
    read_multiple_files
]

# SUPERVISOR_TOOLS = ALL_TOOLS
# ECONPAPER_TOOLS = [tavily_search, tavily_extract, linkup_search, linkup_fetch, convert_pdf_url, convert_pdf_file, read_text_file, read_multiple_files, sequential_thinking]
# ECONQUANT_TOOLS = [run_code_py, run_code_r, sequential_thinking]
# EXPLAINER_TOOLS = [run_code_py, sequential_thinking, tavily_search, linkup_search, tavily_extract, linkup_fetch, read_text_file, read_multiple_files]
# MARKETDEF_TOOLS = [run_code_py, run_code_r, sequential_thinking]
# DOCANALYZER_TOOLS = [convert_pdf_file, convert_pdf_url, tavily_extract, linkup_fetch, read_text_file, read_multiple_files, sequential_thinking]
# CASELAW_TOOLS = [convert_pdf_file, convert_pdf_url, tavily_extract, linkup_fetch, read_text_file, read_multiple_files, sequential_thinking]
# SYNTHESIS_TOOLS = [sequential_thinking]
# REMEDIATION_TOOLS = []
# TEAMFORMATION_TOOLS = [sequential_thinking]
# DEBATE_TOOLS = ALL_TOOLS
SUPERVISOR_TOOLS = ALL_TOOLS
ECONPAPER_TOOLS = ALL_TOOLS
ECONQUANT_TOOLS = ALL_TOOLS
EXPLAINER_TOOLS = ALL_TOOLS
MARKETDEF_TOOLS = ALL_TOOLS
DOCANALYZER_TOOLS = ALL_TOOLS
CASELAW_TOOLS = ALL_TOOLS
SYNTHESIS_TOOLS = ALL_TOOLS
REMEDIATION_TOOLS = ALL_TOOLS
TEAMFORMATION_TOOLS = ALL_TOOLS
DEBATE_TOOLS = ALL_TOOLS
VERIFIER_TOOLS = ALL_TOOLS


pro_prompt = DEBATE_TEAM_PROMPT.replace("[Pro/Con]", "Pro")
con_prompt = DEBATE_TEAM_PROMPT.replace("[Pro/Con]", "Con")

# Agent factories
# Create all agents using their respective models, prompts, and tools
agents = {
    "supervisor": create_agent("supervisor", SUPERVISOR_MODEL, SUPERVISOR_PROMPT, SUPERVISOR_TOOLS),
    "econpaper": create_agent("econpaper", ECONPAPER_MODEL, ECONPAPER_PROMPT, ECONPAPER_TOOLS),
    "econquant": create_agent("econquant", ECONQUANT_MODEL, ECONQUANT_PROMPT, ECONQUANT_TOOLS),
    "explainer": create_agent("explainer", EXPLAINER_MODEL, EXPLAINER_PROMPT, EXPLAINER_TOOLS),
    "marketdef": create_agent("marketdef", MARKETDEF_MODEL, MARKETDEF_PROMPT, MARKETDEF_TOOLS),
    "docanalyzer": create_agent("docanalyzer", DOCANALYZER_MODEL, DOCANALYZER_PROMPT, DOCANALYZER_TOOLS),
    "caselaw": create_agent("caselaw", CASELAW_MODEL, CASELAW_PROMPT, CASELAW_TOOLS),
    "synthesis": create_agent("synthesis", SYNTHESIS_MODEL, SYNTHESIS_PROMPT, SYNTHESIS_TOOLS),
    "remediation": create_agent("remediation", REMEDIATION_MODEL, REMEDIATION_PROMPT, REMEDIATION_TOOLS),
    "teamformation": create_agent("teamformation", TEAMFORMATION_MODEL, TEAMFORMATION_PROMPT, TEAMFORMATION_TOOLS),
    "pro": create_agent("pro", DEBATE_PRO_MODEL, pro_prompt, DEBATE_TOOLS),
    "con": create_agent("con", DEBATE_CON_MODEL, con_prompt, DEBATE_TOOLS),
    "arbiter": create_agent("arbiter", DEBATE_ARBITER_MODEL, ARBITER_PROMPT, DEBATE_TOOLS),
    "verifier": create_agent("verifier", VERIFIER_MODEL, VERIFIER_PROMPT, VERIFIER_TOOLS),
}