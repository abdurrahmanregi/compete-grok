# CompeteGrok

CompeteGrok is an AI-powered system for Industrial Organization (IO) economics and competition law analysis. It uses a multi-agent architecture orchestrated by LangGraph to provide comprehensive, evidence-based insights on complex economic and legal queries.

## Project Overview

CompeteGrok is designed to assist in antitrust and competition economics analysis by leveraging specialized AI agents. It adheres to governing principles including jurisdictional specificity (defaulting to US FTC/DOJ and EU Competition guidelines), declaration of legal standards (e.g., Consumer Welfare Standard), distinction between positive and normative statements, evidence hierarchy (binding case law, peer-reviewed studies, etc.), structured outputs, and hypothesis-driven reasoning. For detailed agent definitions and prompts, refer to AGENTS.md.

## Key Features

- **Multi-Agent Orchestration**: Specialized agents for research, quantitative analysis, explanations, market definitions, document analysis, case law, and debates.
- **Dynamic Agent Composition**: Tailored teams assembled based on query requirements for optimal efficiency.
- **Debate Subgraph**: Balanced pro/con debates with arbiter synthesis for controversial topics.
- **Error Handling & Resilience**: Retry logic, remediation agents, and graceful failure recovery.
- **LaTeX Math Support**: Inline `\(...\)` and display `\[...\]` rendering in outputs.
- **Privacy-First**: Ephemeral processing with no data retention.
- **Extensibility**: MCP tools for search, code execution, PDF processing, and filesystem access.
- **Verification Workflow**: Mandatory fact-checking of all citations by a dedicated Verifier agent.

## Architecture Overview

CompeteGrok leverages LangGraph for workflow orchestration:

- **Managing Partner Agent**: Central orchestrator for query classification, routing, state management, and synthesis.
- **Specialized Agents**: Domain-specific agents (e.g., Economic Research Associate, Quantitative Analyst) performing targeted tasks.
- **Tools Integration**: MCP tools for external capabilities like Tavily search, Linkup deep web searches, code execution (Python/R), PDF conversion, and `fetch_paper_content` for robust academic paper retrieval.
- **State Management**: TypedDict-based tracking of iterations, routing history, sources, and errors to prevent loops.

Workflow: Query → Classification → Agent Routing → Execution → Verification → Debate (if needed) → Synthesis → Report Generation.

## Agent Workflows

Agents follow hypothesis-driven workflows tailored to their roles:
- **Economic Research**: Search and synthesize papers using tools like `tavily_search`, `linkup_search`, and `fetch_paper_content`.
- **Quantitative Analysis**: Perform calculations (e.g., HHI, GUPPI) with `run_code_py`/`r`.
- **Explanation**: Break down models with caveats and LaTeX derivations.
- **Market Definition**: Apply SSNIP tests under jurisdictional guidelines.
- **Document Analysis**: Process uploads via PDF conversion and reading tools.
- **Case Law**: Search and verify precedents.
- **Debate**: Pro/con arguments with arbiter synthesis.
- **Verification**: The **Verifier Agent** checks every citation against external sources (Tavily/Linkup) to ensure accuracy. This is a mandatory step before synthesis.
- **Synthesis**: Integrate results into final reports.
For detailed prompts and routing triggers, see AGENTS.md.

## Installation and Setup

### Prerequisites
- Python 3.8+
- Pandoc (for PDF generation): [Install here](https://pandoc.org/installing.html)
- XeLaTeX (for LaTeX rendering): Included with TeX Live or MiKTeX

### Dependencies
```bash
pip install -r requirements.txt
```

### API Keys and Configuration
1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your API keys:
   - `XAI_API_KEY`: xAI Grok API key
   - `TAVILY_API_KEY`: Tavily search API key
   - `MISTRAL_API_KEY`: Mistral API key for PDF processing
   - `LINKUP_API_KEY`: Linkup API key for deep web searches
   - `LANGCHAIN_API_KEY`: LangSmith API key (optional, for tracing)

3. Ensure external MCP tools are accessible (paths configured in `config.py`; adjust for your OS).

### Configuration
The system behavior can be fine-tuned in `config.py`:

- **STRICT_MODE**: When set to `True` (default), tools will raise exceptions on failure rather than returning mock data. This ensures that the system only relies on actual, successful tool executions.
- **Logging**: Configurable log levels (DEBUG/INFO) and file paths in `compete_logging.py`.

### Verification
Run the help command:
```bash
python app.py --help
```

## Usage

### Basic Usage
```bash
python app.py --query "Calculate HHI for a market with firms of sizes 30%, 25%, 20%, 15%, 10%"
```

### Advanced Options
- `--query`: Query text or path to .txt file (supports multi-line queries and embedded file references).
- `--file`: PDF/Excel uploads for analysis (multiple files allowed).
- `--verbose`: Detailed logging.
- `--output-dir`: Output directory (default: `./outputs`).
- `--debate`: Forces debate module.

### Examples
1. Simple query:
   ```bash
   python app.py --query "Explain the Lerner Index"
   ```

2. File-based query:
   ```bash
   python app.py --query inputs/query_01.txt --verbose --output-dir ./reports
   ```

3. Document analysis with debate:
   ```bash
   python app.py --query "Analyze this merger" --file merger_doc.pdf --debate
   ```

4. Multi-file upload:
   ```bash
   python app.py --query "Compare these cases" --file case1.pdf case2.pdf
   ```

5. Query file with embedded files:
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
   ```bash
   python app.py --query query_with_files.txt
   ```

## Agents Overview

- **Managing Partner**: Orchestrates queries, routes agents, manages state.
- **Economic Research Associate**: Searches and synthesizes academic papers.
- **Quantitative Analyst**: Performs calculations (HHI, UPP, GUPPI) and simulations.
- **Educational Specialist**: Explains models with caveats and derivations.
- **Market Definition Expert**: Defines markets using SSNIP tests.
- **Document Analyst**: Analyzes uploaded documents.
- **Legal Precedent Specialist**: Searches case law and precedents.
- **Debate Facilitators**: Pro/Con advocates and Arbiter for balanced debates.
- **Synthesis Specialist**: Integrates outputs into final reports.
- **Verifier**: Fact-checks citations.
- **Remediation**: Handles errors and recovery.

For detailed prompts and routing, see `AGENTS.md`.

## Contribution Guidelines

We welcome contributions to CompeteGrok! To contribute:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/YourFeature`).
3. Commit your changes (`git commit -m 'Add YourFeature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a Pull Request.

Please ensure your code follows Python best practices, includes docstrings, and passes tests. For major changes, open an issue first to discuss. See AGENTS.md for agent-specific guidelines.

## Governing Principles

- **Jurisdictional Specificity**: Considers relevant jurisdictions (e.g., US FTC/DOJ, EU Competition) and guidelines.
- **Evidence Hierarchy**: Prioritizes binding case law, peer-reviewed empirics, agency guidelines, persuasive case law, reputable reports.
- **Hypothesis-Driven Reasoning**: Formulates and tests hypotheses sequentially.
- **Truth-Seeking**: Bases responses on verified facts; avoids hallucinations.

## Output Structure

- **Markdown Report**: Includes query, routes, synthesis, references.
- **PDF Report**: Rendered with LaTeX math via Pandoc/XeLaTeX.
- **Sources**: Numbered list of citations with URLs/titles.

## Limitations and Notes

- Not legal advice; verify data recency.
- Computational timeouts for complex simulations.
- Models: xAI Grok variants.
- Contributing: See `AGENTS.md` for prompts; `graph.py` for architecture.
- Troubleshooting: Check logs; ensure API keys and tools are configured.

For more details, refer to `AGENTS.md`.

## Change Log

### Recent Improvements
- Step 1: Initial analysis and planning of core architecture.
- Step 2: Implementation of multi-agent orchestration using LangGraph.
- Step 3: Integration of MCP tools for search, code execution, and PDF processing.
- Step 4: Development of specialized agents with hypothesis-driven prompts.
- Step 5: Addition of debate subgraph for balanced analysis.
- Step 6: Incorporation of error handling, remediation, and verification agents.

### Runtime Fixes
- Added advanced logging in [`compete_logging.py`](compete_logging.py).
- Fixed SDK alignments in tools/ directory for consistent API integrations.
- Resolved runtime errors in agent routing and tool executions.
- Implemented loop prevention and state management fixes as documented in [`loop_prevention_fixes.md`](loop_prevention_fixes.md).
- End-to-end tested with sample queries like [`query_01.txt`](inputs/query_01.txt).

### Current State
- Enhanced modularity with dynamic agent composition and extensible tools.
- Achieved 54% test coverage across key components.
- Project runs error-free in standard configurations.
- Key files added/updated: [`AGENTS.md`](AGENTS.md), [`graph.py`](graph.py), [`debate.py`](debate.py), [`compete_logging.py`](compete_logging.py), and various agents in agents/ directory.
