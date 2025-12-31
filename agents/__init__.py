from typing import Any, List, Optional

from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.prebuilt import create_react_agent

from config import *
from tools import *


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
        # Extract the last message content for mock response personalization
        last_message = messages[-1].content if messages else ""
        mock_content = rf"""Hypothesis: Analyzed '{last_message}' → {self.model_name} task (e.g., HHI calc, SSNIP sim).

Used sequential_thinking. Tools: run_code_py/r for quants, tavily_search for papers.

Output: \[ HHI = \sum_i s_i^2 \]

Reflection: Hypothesis tested; caveats (2025 data, IIA fails); robust via mocks."""
        # Create a chat generation with the mock content
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
    # Log the agent creation details
    print(f"Creating agent '{name}' with model '{model}' and system_prompt length {len(system_prompt)}")
    # Retrieve sampling parameters for the agent or use default
    sampling = SAMPLING_PARAMS.get(name, SAMPLING_PARAMS["default"])
    if not XAI_API_KEY:
        # Use mock model if no API key is available
        llm = MockChatModel(model_name=model, **sampling)
    else:
        # Use real ChatOpenAI with xAI API
        llm = ChatOpenAI(
            model=model,
            api_key=XAI_API_KEY,
            base_url="https://api.x.ai/v1",
            **sampling
        )
    # Create the prompt template with system prompt and message placeholder
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ])
    # Create and return the react agent
    return create_react_agent(llm, tools, prompt=prompt)


# Tool bindings
# List of all available tools for agents
ALL_TOOLS = [
    run_code_py,  # Tool for running Python code
    run_code_r,   # Tool for running R code
    tavily_search,  # Broad search tool
    tavily_extract, # Extraction from search results
    linkup_search,  # Deep analysis search
    linkup_fetch,   # Fetching content
    sequential_thinking,  # For sequential reasoning
    convert_pdf_url,  # Convert PDF from URL to Markdown
    convert_pdf_file, # Convert local PDF to Markdown
    read_text_file,   # Read single text file
    read_multiple_files,  # Read multiple text files
    fetch_paper_content  # Smart wrapper for fetching paper content (PDF/HTML)
]

# Import agent creation functions
from .supervisor import create_supervisor_agent
from .econpaper import create_econpaper_agent
from .econquant import create_econquant_agent
from .explainer import create_explainer_agent
from .marketdef import create_marketdef_agent
from .docanalyzer import create_docanalyzer_agent
from .caselaw import create_caselaw_agent
from .synthesis import create_synthesis_agent
from .verifier import create_verifier_agent
from .remediation import create_remediation_agent
from .pro import create_pro_agent
from .cons import create_cons_agent
from .arbiter import create_arbiter_agent
from .teamformation import create_teamformation_agent

# Dictionary of all agents, created with their specific configurations
agents = {
    "supervisor": create_supervisor_agent(),
    "econpaper": create_econpaper_agent(),
    "econquant": create_econquant_agent(),
    "explainer": create_explainer_agent(),
    "marketdef": create_marketdef_agent(),
    "docanalyzer": create_docanalyzer_agent(),
    "caselaw": create_caselaw_agent(),
    "synthesis": create_synthesis_agent(),
    "verifier": create_verifier_agent(),
    "remediation": create_remediation_agent(),
    "pro": create_pro_agent(),
    "cons": create_cons_agent(),
    "arbiter": create_arbiter_agent(),
    "teamformation": create_teamformation_agent(),
}