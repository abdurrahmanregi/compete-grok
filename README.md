# CompeteGrok

CompeteGrok is an advanced AI-powered system designed for Industrial Organization (IO) economics and competition law analysis. It leverages a multi-agent architecture orchestrated by LangGraph to provide comprehensive, truth-seeking insights on complex economic and legal queries. The system integrates specialized agents for research, quantitative analysis, explanations, market definitions, document analysis, case law searches, and balanced debates, ensuring thorough and nuanced responses.

## Installation and Setup

### Prerequisites
- Python 3.8+
- Pandoc (for PDF generation): Install from [https://pandoc.org/installing.html](https://pandoc.org/installing.html)
- XeLaTeX (for LaTeX rendering in PDFs): Included with most LaTeX distributions like TeX Live or MiKTeX

### Dependencies
Install Python dependencies:
```bash
pip install -r requirements.txt
```

### API Keys and Configuration
1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your API keys:
    - `XAI_API_KEY`: Your xAI Grok API key
    - `TAVILY_API_KEY`: Tavily search API key
    - `MISTRAL_API_KEY`: Mistral API key for PDF processing
    - `LINKUP_API_KEY`: Linkup API key for deep web searches
    - `LANGCHAIN_API_KEY`: LangSmith API key for optional tracing (currently not implemented in code)

3. Ensure external MCP tools are accessible (paths configured in `config.py` for Windows; adjust for other OS).

### Verification
Run the help command to verify setup:
```bash
python app.py --help
```

## Architecture Schematic

CompeteGrok uses a LangGraph-based orchestration system with the following components:

### Core Architecture
- **Managing Partner Agent**: Central orchestrator that classifies queries, routes to specialized agents, manages state, and synthesizes final outputs.
- **Specialized Agents**: Domain-specific agents (Economic Research Associate, Quantitative Analyst, Educational Specialist, etc.) that perform targeted tasks.
- **Debate Subgraph**: A separate workflow for pro/con debates with an arbiter for balanced analysis.
- **Tools Integration**: MCP (Model Context Protocol) tools for external capabilities like search, code execution, and PDF processing.
- **State Management**: TypedDict-based state tracking iteration counts, routing history, sources, and debate rounds to prevent loops.

### Workflow Flow
```
Query Input → Managing Partner Classification → Agent Routing → Parallel/Serial Execution → Debate (if needed) → Synthesis → Report Generation
```

Key features:
- **Loop Prevention**: Iteration limits (max 5), routing history checks, and completion signals prevent infinite cycles.
- **Multi-Round Debates**: Iterative debate workflow informed by agent outputs.
- **Ephemeral RAG**: Document uploads processed without retention for privacy.
- **LaTeX Math Support**: Inline `\(...\)` and display `\[...\]` math rendering in outputs.

## Dynamic Agent Composition

CompeteGrok features dynamic agent composition, allowing the system to assemble tailored teams of specialized agents based on the specific requirements of each query. This adaptive approach ensures optimal resource allocation and comprehensive analysis.

### How It Works

1. **Query Analysis**: The Team Formation Agent analyzes the incoming query to identify key elements such as topics, required expertise, and complexity.
2. **Agent Selection**: Based on predefined triggers and relevance criteria, the agent selects the most appropriate combination of specialized agents from the available pool (e.g., Economic Research Associate, Quantitative Analyst, Educational Specialist).
3. **Team Assembly**: The selected agents are dynamically composed into a collaborative team, with the Managing Partner Agent overseeing coordination and workflow.
4. **Execution and Synthesis**: The team executes their tasks in parallel or sequentially as needed, with results synthesized into a cohesive final output.

### Benefits

- **Efficiency**: Only relevant agents are activated, reducing computational overhead and response time.
- **Relevance**: Tailored agent combinations ensure comprehensive coverage of query-specific aspects.
- **Scalability**: Easily accommodates new agents and query types without manual reconfiguration.
- **Flexibility**: Adapts to complex, multi-disciplinary queries requiring diverse expertise.

### Integration with Existing Features

Dynamic agent composition integrates seamlessly with CompeteGrok's core architecture:

- **Managing Partner Integration**: The Managing Partner Agent can leverage the Team Formation Agent for initial routing decisions.
- **Debate Subgraph**: Selected teams can include debate facilitators for controversial topics.
- **Error Handling**: The RemediationAgent can adjust team composition in response to failures.
- **State Management**: Team composition is tracked in the AgentState for loop prevention and workflow continuity.

This feature enhances the system's ability to handle diverse and evolving query patterns in IO economics and competition law analysis.

## Enhanced Error Handling and Resilience

CompeteGrok incorporates robust error handling mechanisms to ensure reliable operation and graceful recovery from failures. These features prevent workflow interruptions due to transient issues like API timeouts or tool failures, improving overall system resilience.

### Tenacity Wrappers (`tools/wrappers.py`)
- **Function**: Provides retry logic with exponential backoff for external MCP tools.
- **Implementation**: Uses the `tenacity` library to wrap functions like `tavily_search`, `linkup_search`, `linkup_fetch`, `tavily_extract`, and `convert_pdf_url`.
- **Behavior**: Retries failed operations up to 3 times with increasing delays (1-10 seconds). Raises `ToolExecutionError` if all retries fail (detected by "Mock" in response indicating failure).
- **Reliability Improvement**: Handles transient network issues or API rate limits without halting the workflow, ensuring consistent tool availability.

### RemediationAgent (`agents/agents.py`)
- **Role**: Specialized agent for handling tool and agent failures, enabling recovery strategies.
- **Model**: grok-4-1-fast-reasoning (xAI)
- **Capabilities**: Analyzes error messages and decides on remediation actions: rephrase queries, fallback to alternative tools, or abort unrecoverable tasks.
- **Interaction**: Activated when agents encounter exceptions; outputs JSON decisions for routing adjustments.
- **Reliability Improvement**: Allows dynamic adaptation to failures, such as switching from a failing search tool to an alternative, maintaining workflow continuity.

### Graph Updates for Error Handling (`graph.py`)
- **State Enhancements**: Added `last_error`, `remediation_decision`, and `last_agent` fields to `AgentState` for error tracking.
- **Conditional Routing**: Agents route to `remediation` on exceptions instead of failing. Remediation routes based on decisions: rephrase (back to failing agent), fallback (to supervisor), or abort (to END).
- **Exception Handling**: All agent nodes wrapped in try-except blocks to capture and propagate errors without crashing the graph.
- **Reliability Improvement**: Enables graceful degradation and recovery, preventing single-point failures from stopping complex multi-agent workflows. Supports iterative error resolution while maintaining state integrity.

## Agents Overview

### Managing Partner Agent
- **Role**: Central orchestrator for query classification, agent routing, state management, and final synthesis.
- **Model**: grok-4-1-fast-reasoning (xAI)
- **Capabilities**: Planning, reflection, coordination; uses sequential thinking for hypothesis testing.
- **Interaction**: Routes queries to agents based on triggers; monitors completion and prevents loops.

### Economic Research Associate Agent
- **Role**: Searches, extracts, and synthesizes academic papers on IO economics.
- **Model**: grok-4-1-fast-reasoning (xAI)
- **Capabilities**: PDF handling, synthesis; prioritizes 2025 papers and highlights biases.
- **Tools**: tavily-search/extract, linkup-search/fetch, convert_pdf_url/file, read_text_file, read_multiple_files, sequential_thinking.
- **Triggers**: "paper", "NBER", "research", "CEPR", "arXiv", "econometrics".
- **Interaction**: Feeds research insights to other agents; reflects on results.

### Quantitative Analyst Agent
- **Role**: Performs quantitative calculations and simulations.
- **Model**: grok-4-0709 (xAI)
- **Capabilities**: Math/coding for HHI, UPP, GUPPI calculations; explains with LaTeX.
- **Tools**: run_code_py, run_code_r, sequential_thinking.
- **Triggers**: Quantitative tasks, simulations, math.
- **Interaction**: Provides numerical results for synthesis; addresses computational limits.

### Educational Specialist Agent
- **Role**: Breaks down models with caveats and step-by-step derivations.
- **Model**: grok-4-0709 (xAI)
- **Capabilities**: Educational explanations; adaptive language; LaTeX derivations.
- **Tools**: run_code_py, sequential_thinking.
- **Triggers**: "explain", "caveats".
- **Interaction**: Clarifies concepts; uses completion signals like "This completes the explanation".

### Market Definition Expert Agent
- **Role**: Defines markets using SSNIP and hypothetical analyses.
- **Model**: grok-4-0709 (xAI)
- **Capabilities**: Boundary hypotheses; simulates market tests.
- **Tools**: run_code_py, run_code_r, sequential_thinking.
- **Triggers**: "market definition", "SSNIP".
- **Interaction**: Informs competition analyses; notes data recency issues.

### Document Analyst Agent
- **Role**: Analyzes uploaded documents for insights.
- **Model**: grok-4-1-fast-reasoning (xAI)
- **Capabilities**: RAG/vision on PDFs; ephemeral processing.
- **Tools**: convert_pdf_file/url, tavily-extract, linkup-fetch, read_text_file, read_multiple_files, sequential_thinking.
- **Triggers**: "analyze document", file uploads.
- **Interaction**: Extracts implications; auto-deletes for privacy.

### Legal Precedent Specialist Agent
- **Role**: Searches precedents and case law.
- **Model**: grok-4-1-fast-reasoning (xAI)
- **Capabilities**: Recency-focused legal research.
- **Tools**: tavily-search, linkup-search, sequential_thinking.
- **Triggers**: "case law", "precedent", "FTC", "EC Competition", "US DoJ Antitrust".
- **Interaction**: Provides legal context; notes jurisdictional caveats.

### Debate Facilitators
- **Role**: Conducts balanced pro/con debates.
- **Models**: grok-4-0709 (xAI) for Pro, Con, and Arbiter.
- **Capabilities**: Evidence-based arguments; iterative rounds.
- **Tools**: All available tools.
- **Triggers**: "debate", "pro/con"; forced via `--debate` flag.
- **Interaction**: Pro and Con advocate positions; Arbiter synthesizes; informs multi-round workflows.

### Synthesis Specialist
- **Role**: Integrates all agent outputs into comprehensive insights.
- **Model**: grok-4-0709 (xAI)
- **Capabilities**: Coherence, reflection; aggregates sources.
- **Tools**: sequential_thinking.
- **Triggers**: Final integration tasks.
- **Interaction**: Reviews conversation history; provides complete, self-contained answers.

## CLI Usage

### Basic Usage
```bash
python app.py --query "Calculate HHI for a market with firms of sizes 30%, 25%, 20%, 15%, 10%"
```

### Advanced Options
- `--query`: Query text or path to .txt file (supports multi-line queries and QUERY/FILES sections for embedded file references).
- `--file`: PDF/Excel uploads for RAG (multiple files allowed).
- `--verbose`: Enables detailed logging.
- `--output-dir`: Specifies output directory (default: `./outputs`).
- `--debate`: Forces debate module regardless of supervisor routing.

### Examples
1. Simple query:
   ```bash
   python app.py --query "Explain the Lerner Index"
   ```

2. File-based query with verbose output:
   ```bash
   python app.py --query inputs/hhi.txt --verbose --output-dir ./reports
   ```

3. Document analysis with debate:
   ```bash
   python app.py --query "Analyze this merger" --file merger_doc.pdf --debate
   ```

4. Multi-file upload:
   ```bash
   python app.py --query "Compare these cases" --file case1.pdf case2.pdf
   ```

5. Query file with embedded file references:
    ```bash
    python app.py --query query_with_files.txt
    ```
    Where `query_with_files.txt` contains:
    ```
    QUERY:
    """
    Analyze the merger in these documents
    """
    FILES:
    """
    merger_doc.pdf
    financial_data.xlsx
    """
    ```

6. Complex query file with multi-line instructions and multiple files:
    ```bash
    python app.py --query "inputs/complex_query.txt"
    ```
    Where `inputs/complex_query.txt` contains:
    ```
    QUERY:
    """
    Analyze the competitive effects of this merger using IO logics.
    Debate the potential anticompetitive concerns.
    Provide quantitative analysis and legal precedents.
    """
    FILES:
    """
    merger_agreement.pdf
    market_data.xlsx
    financial_statements.pdf
    competition_analysis.docx
    """
    ```

## Workflow Explanation

1. **Query Processing**: Input query parsed; documents converted to Markdown if uploaded.
2. **Managing Partner Classification**: Managing Partner analyzes query, classifies type, and routes to relevant agents (e.g., Quantitative Analyst for calculations, Economic Research Associate for research).
3. **Agent Execution**: Agents run in parallel/serial based on dependencies; use tools for external data/code execution.
4. **Debate Integration**: If controversy detected or `--debate` used, debate subgraph runs iterative rounds informed by agent outputs.
5. **Synthesis**: SynthesisAgent aggregates all insights, sources, and caveats into a final comprehensive response.
6. **Report Generation**: Output saved as Markdown (with LaTeX math fixed) and PDF (via Pandoc/XeLaTeX); includes references, privacy notes, and disclaimers.

### Loop Prevention
- Iteration count limits (max 5 total).
- Routing history prevents same agent twice.
- Completion signals (e.g., "This completes the explanation") trigger synthesis.
- Confidence thresholds and debate forcing for unresolved queries.

### Output Structure
- **Markdown Report**: Query, timestamp, routes, synthesis, references.
- **PDF Report**: Rendered version with LaTeX math.
- **Sources**: Numbered list of URLs/titles from all agents.
- **Privacy**: Ephemeral processing; no data retention.

## Governing Principles

CompeteGrok operates under the following core principles to ensure rigorous, evidence-based analysis:

- **Jurisdictional Specificity**: All analyses consider relevant jurisdictions (e.g., US FTC/DOJ, EU Competition) and their specific guidelines.
- **Evidence Hierarchy & Citations**: Prioritizes primary sources (statutes, case law, empirical data) over secondary; cites sources with URLs/titles in a 'Sources' section.
- **Structured Outputs**: Uses JSON-like structured formats for outputs where appropriate, e.g., {"hypothesis": "...", "evidence": "...", "conclusion": "..."}.
- **Hypothesis-Driven Reasoning**: Formulates and tests hypotheses sequentially, reflecting on results.

## Key Principles and Features

- **Truth-Seeking**: Bases responses on verified facts; prioritizes 2025 data; avoids hallucinations.
- **LaTeX Math**: Consistent use of `\(...\)` inline and `\[...\]` display for equations (e.g., \( HHI = \sum s_i^2 \)).
- **Loop Prevention**: State-based mechanisms prevent infinite routing cycles.
- **Multi-Agent Orchestration**: Specialized agents collaborate for comprehensive analysis.
- **Debate for Balance**: Pro/con arguments ensure nuanced viewpoints on controversial topics.
- **Privacy-First**: Ephemeral RAG; auto-deletion of uploads.
- **Extensibility**: MCP tools enable easy addition of new capabilities.
- **Error Handling**: Reflection and caveats for API failures or data issues.

### Filesystem MCP Integration

CompeteGrok integrates filesystem MCP tools for enhanced document processing capabilities:

- **read_text_file**: Reads the contents of a single text file, enabling agents to access and analyze local documents directly.
- **read_multiple_files**: Reads multiple text files simultaneously, allowing efficient batch processing of document collections.

These tools support the system's ephemeral RAG functionality, enabling agents like EconPaper and DocAnalyzer to process converted PDF Markdown files and other text-based documents without retaining data.

## Additional Notes

- **Models**: All powered by xAI Grok variants for deep reasoning and math capabilities.
- **Tools**: Integrates Tavily (search), Linkup (deep web), code execution (Python/R), PDF conversion (Mistral OCR), filesystem access (read_text_file, read_multiple_files), and sequential thinking.
- **Limitations**: Not legal advice; verify data recency; computational timeouts for complex simulations.
- **Contributing**: See AGENTS.md for prompt engineering; graph.py for architecture modifications.
- **Troubleshooting**: Check logs for errors; ensure API keys and external tools are configured.

For more details on agent prompts and routing, refer to `AGENTS.md`.