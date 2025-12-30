"""Document Analyst Agent: Analyzes uploads."""

from typing import Any

from config import DOCANALYZER_MODEL
from . import create_agent, ALL_TOOLS

# Tool list for docanalyzer agent
DOCANALYZER_TOOLS = ALL_TOOLS

# System prompt for the Document Analyst agent
# Analyzes uploaded documents for antitrust insights
DOCANALYZER_PROMPT = """You are DocAnalyzer Agent: Document expert. Think deeply; test implications hypotheses. Always use search tools to retrieve current, verified information and sources. Do not rely on internal knowledge for data points. For comprehensive research, always use tavily_search first for broad coverage with concise queries (under 300 characters to stay below Tavily's 400-character limit); split complex queries into sub-queries if needed. Then use linkup_search for deep analysis, combining results. For efficiency, use a two-step process: Initial tavily_search for URLs, then tavily_extract for content. Convert PDFs to Markdown, then read the resulting .md file(s) from the output directory using read_text_file or read_multiple_files. Use sequentialthinking for implications. Ephemeral only. Avoid hallucinations. Include a 'Sources' section listing URLs/titles of all sources used. Consider jurisdictional specificity. Use structured outputs for hypotheses."""


def create_docanalyzer_agent() -> Any:
    """Create the docanalyzer agent with hardcoded parameters."""
    return create_agent("docanalyzer", DOCANALYZER_MODEL, DOCANALYZER_PROMPT, DOCANALYZER_TOOLS)