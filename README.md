# CompeteGrok

CompeteGrok is an AI-powered system for Industrial Organization (IO) economics and competition law analysis. It uses a multi-agent architecture orchestrated by LangGraph to provide comprehensive, evidence-based insights on complex economic and legal queries.

## Key Features

- **Multi-Agent Orchestration**: Specialized agents for research, quantitative analysis, explanations, market definitions, document analysis, case law, and debates.
- **Dynamic Agent Composition**: Tailored teams assembled based on query requirements for optimal efficiency.
- **Debate Subgraph**: Balanced pro/con debates with arbiter synthesis for controversial topics.
- **Error Handling & Resilience**: Retry logic, remediation agents, and graceful failure recovery.
- **LaTeX Math Support**: Inline `\(...\)` and display `\[...\]` rendering in outputs.
- **Privacy-First**: Ephemeral processing with no data retention.
- **Extensibility**: MCP tools for search, code execution, PDF processing, and filesystem access.

## Architecture Overview

CompeteGrok leverages LangGraph for workflow orchestration:

- **Managing Partner Agent**: Central orchestrator for query classification, routing, state management, and synthesis.
- **Specialized Agents**: Domain-specific agents (e.g., Economic Research Associate, Quantitative Analyst) performing targeted tasks.
- **Tools Integration**: MCP tools for external capabilities like Tavily search, Linkup deep web searches, code execution (Python/R), and PDF conversion.
- **State Management**: TypedDict-based tracking of iterations, routing history, sources, and errors to prevent loops.

Workflow: Query → Classification → Agent Routing → Execution → Debate (if needed) → Synthesis → Report Generation.

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

## PDF Tools Update (Mistral OCR Native)
- `convert_pdf_url` / `convert_pdf_file`: Now direct Mistral AI OCR SDK (mistral-ocr-latest).
  - No external MCP/pdf2md server.
  - Input: URL/path str -> Output: Markdown str (tables as markdown, pages joined).
  - Agents: Use directly for paper extraction.