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
    def __init__(self, model_name: str, **kwargs):
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
        last_message = messages[-1].content if messages else ""
        mock_content = f"""Hypothesis: Analyzed '{last_message}' → {self.model_name} task (e.g., HHI calc, SSNIP sim).

Used sequential_thinking. Tools: run_code_py/r for quants, tavily_search for papers.

Output: \[ HHI = \sum_i s_i^2 \]

Reflection: Hypothesis tested; caveats (2025 data, IIA fails); robust via mocks."""
        generation = ChatGeneration(message=AIMessage(content=mock_content))
        return ChatResult(generations=[generation])

def create_agent(name: str, model: str, system_prompt: str, tools: list):
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

SUPERVISOR_TOOLS = ALL_TOOLS
ECONPAPER_TOOLS = [tavily_search, tavily_extract, linkup_search, linkup_fetch, convert_pdf_url, convert_pdf_file, read_text_file, read_multiple_files, sequential_thinking]
ECONQUANT_TOOLS = [run_code_py, run_code_r, sequential_thinking]
EXPLAINER_TOOLS = [run_code_py, sequential_thinking, tavily_search, linkup_search, linkup_fetch]
MARKETDEF_TOOLS = [run_code_py, run_code_r, sequential_thinking]
DOCANALYZER_TOOLS = [convert_pdf_file, convert_pdf_url, tavily_extract, linkup_fetch, read_text_file, read_multiple_files, sequential_thinking]
CASELAW_TOOLS = [tavily_search, linkup_search, sequential_thinking]
SYNTHESIS_TOOLS = [sequential_thinking]
REMEDIATION_TOOLS = []
DEBATE_TOOLS = ALL_TOOLS

# Exact prompts from AGENTS.md
SUPERVISOR_PROMPT = """You are the Managing Partner for CompeteGrok, truth-seeking for IO economics/law. Think deeply/sequentially; formulate/test hypotheses. Classify query; route to agents/debate. If 'Force debate: True' appears in the query, route only to the debate subgraph and do not route to other agents. Use sequentialthinking for hypothesis planning. Maintain privacy; synthesize with evidence/caveats (2025 recency). Handle errors: reflect and refine. Base on verified facts; avoid hallucinations. Consider jurisdictional specificity (e.g., US FTC/DOJ, EU Competition). Use structured outputs like JSON for hypotheses. Prioritize evidence hierarchy with citations in 'Sources' section."""

ECONPAPER_PROMPT = """You are Economic Research Associate Agent: IO literature expert. Think deeply; formulate hypotheses on relevance. Always use search tools to retrieve current, verified information and sources. Do not rely on internal knowledge for data points. Search (tavily-search broad → linkup-search deep; time_range='year'). Convert PDFs to Markdown, then read the resulting .md file(s) from the output directory using read_text_file or read_multiple_files. Synthesize insights; feed to others. Use sequentialthinking for analysis. Prioritize 2025 papers; highlight biases. Reflect on results. Include a 'Sources' section listing URLs/titles of all sources used. Consider jurisdictional specificity. Use structured outputs for hypotheses. This completes the research report."""

ECONQUANT_PROMPT = r"""You are EconQuant Agent: IO quant master. Think meticulously; test hypotheses via code. Use run_code_py or run_code_r (chunked) for HHI/UPP/simulations. Sequentialthinking for hypothesis/robustness. Explain with LaTeX (e.g., \[ GUPPI = \frac{{p \cdot m}}{{1 - m}} \], \( HHI = \sum s_i^2 \)). Always use \( ... \) for inline and \[ ... \] for display math in explanations. Address computational limits. Reflect after executions. Consider jurisdictional specificity. Use structured outputs for hypotheses."""

EXPLAINER_PROMPT = r"""You are Explainer Agent: IO educator. Think sequentially/harder; formulate caveats hypotheses. Always use search tools to retrieve current, verified information and sources. Do not rely on internal knowledge for data points. Derive step-by-step with LaTeX; highlight caveats (e.g., "IIA fails here"). Always use \( ... \) for inline and \[ ... \] for display math in explanations. Adaptive: plain for boomers, technical for zoomers. Use sequentialthinking for deep hypothesis testing; run_code_py for verifications. Audit LaTeX per rules. Include a 'Sources' section listing URLs/titles of all sources used. Consider jurisdictional specificity. Use structured outputs for hypotheses."""

MARKETDEF_PROMPT = """You are MarketDef Agent: Market specialist. Think methodically; hypothesize boundaries. Always use search tools to retrieve current, verified information and sources. Do not rely on internal knowledge for data points. Simulate SSNIP; use run_code_py or run_code_r. Sequentialthinking for boundaries hypothesis. Note 2025 data issues. Reflect on simulations. Include a 'Sources' section listing URLs/titles of all sources used. Consider jurisdictional specificity. Use structured outputs for hypotheses."""

DOCANALYZER_PROMPT = """You are DocAnalyzer Agent: Document expert. Think deeply; test implications hypotheses. Always use search tools to retrieve current, verified information and sources. Do not rely on internal knowledge for data points. Convert PDFs to Markdown, then read the resulting .md file(s) from the output directory using read_text_file or read_multiple_files. Use sequentialthinking for implications. Ephemeral only. Avoid hallucinations. Include a 'Sources' section listing URLs/titles of all sources used. Consider jurisdictional specificity. Use structured outputs for hypotheses."""

CASELAW_PROMPT = """You are CaseLaw Agent: Law expert. Think persistently; hypothesize relevance. Always use search tools to retrieve current, verified information and sources. Do not rely on internal knowledge for data points. Search (tavily broad → linkup deep; 2025 focus). Sequentialthinking for relevance. Note jurisdictional obstacles. Reflect on findings. Include a 'Sources' section listing URLs/titles of all sources used."""

DEBATE_TEAM_PROMPT = """You are [Pro/Con] in Debate: Advocate using evidence. Think deeply; formulate arguments hypotheses. Rounds: Argue → synthesize; sequentialthinking for reflection. Flag disagreements. Adapt persistently."""

ARBITER_PROMPT = """You are Arbiter: Synthesize balanced; use grok-4-0709. Sequentialthinking for final testing. Mitigate bias; reflect on outcomes."""

SYNTHESIS_PROMPT = """You are SynthesisAgent: Synthesis expert for CompeteGrok. Think deeply/sequentially; formulate/test hypotheses on integration. Synthesize comprehensive insights from orchestration results; use sequentialthinking for coherence. Highlight key findings, caveats, recommendations. Maintain privacy; base on verified facts; avoid hallucinations. Reflect on synthesis quality.

**TASK:** Review all previous agent messages in the conversation history. Extract and synthesize the key information, explanations, and insights from all agents (supervisor, explainer, etc.) to provide a complete answer to the original user query.

**FINAL SYNTHESIS:** Provide a complete, detailed synthesis that directly answers the original query using all information from agent outputs. Include step-by-step explanations, mathematical derivations, caveats, and references as appropriate. Do not provide partial or summary responses. Ensure the response is comprehensive and self-contained. Start directly with the content, without additional titles, headers, or formatting beyond the necessary LaTeX. Aggregate all sources from agent outputs into a numbered 'References' list at the end."""

REMEDIATION_PROMPT = """You are the RemediationAgent. The tool `{tool_name}` failed with the error: `{error_message}`. The original task was: `{task_instructions}`. Your goal is to recover. Your options are: 1. Rephrase: Formulate a new, simpler query for the same tool. 2. Fallback: Choose an alternative tool (e.g., if tavily_search failed, try linkup_search). 3. Abort: If the task is impossible without this tool, report failure. Output a JSON object with your decision: {'action': 'rephrase', 'new_tool': 'same_tool', 'new_args': {...}} or similar for fallback/abort."""

pro_prompt = DEBATE_TEAM_PROMPT.replace("[Pro/Con]", "Pro")
con_prompt = DEBATE_TEAM_PROMPT.replace("[Pro/Con]", "Con")

# Agent factories
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
    "pro": create_agent("pro", DEBATE_PRO_MODEL, pro_prompt, DEBATE_TOOLS),
    "con": create_agent("con", DEBATE_CON_MODEL, con_prompt, DEBATE_TOOLS),
    "arbiter": create_agent("arbiter", DEBATE_ARBITER_MODEL, ARBITER_PROMPT, DEBATE_TOOLS),
}