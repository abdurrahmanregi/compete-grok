from dotenv import load_dotenv
import os
load_dotenv()

# API Keys
XAI_API_KEY = os.getenv('XAI_API_KEY')
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
LINKUP_API_KEY = os.getenv('LINKUP_API_KEY')

# Models from AGENTS.md
SUPERVISOR_MODEL = "grok-4-1-fast-reasoning"
ECONPAPER_MODEL = "grok-4-1-fast-reasoning"
ECONQUANT_MODEL = "grok-4-1-fast-reasoning"
EXPLAINER_MODEL = "grok-4-1-fast-reasoning"
MARKETDEF_MODEL = "grok-4-1-fast-reasoning"
DOCANALYZER_MODEL = "grok-4-1-fast-reasoning"
CASELAW_MODEL = "grok-4-1-fast-reasoning"
SYNTHESIS_MODEL = "grok-4-1-fast-non-reasoning"
REMEDIATION_MODEL = "grok-4-1-fast-non-reasoning"
# Debate Module Agents
DEBATE_PRO_MODEL = "grok-4-1-fast-reasoning"
DEBATE_CON_MODEL = "grok-4-1-fast-reasoning"
DEBATE_ARBITER_MODEL = "grok-4-1-fast-non-reasoning"
TEAMFORMATION_MODEL = "grok-4-1-fast-reasoning"

SAMPLING_PARAMS = {
    "default": {"temperature": 0.1, "top_p": 0.95, "extra_body": {"top_k": 20}},
    "econquant": {"temperature": 0.1, "top_p": 0.95, "extra_body": {"top_k": 20}},
    # "supervisor": {"temperature": 0.5, "top_p": 0.95, "max_tokens": 65536, "extra_body": {"top_k": 20}},
    # "synthesis": {"temperature": 0.6, "top_p": 0.95, "max_tokens": 65536, "extra_body": {"top_k": 20}}
    "supervisor": {"temperature": 0.1, "top_p": 0.95, "extra_body": {"top_k": 20}},
    "synthesis": {"temperature": 0.1, "top_p": 0.95, "extra_body": {"top_k": 20}}
}

# MCP Paths
RUN_CODE_PY_CMD = r"C:\Users\abdur\Documents\python-MCP\venv\Scripts\python.exe"
RUN_CODE_PY_ARGS = ["-u", r"C:\Users\abdur\Documents\python-MCP\run_code_py.py"]
RUN_CODE_PY_ENV = {"EXECUTION_TIMEOUT": "1800"}
RUN_CODE_R_CMD = "Rscript"
RUN_CODE_R_ARGS = [r"C:\Users\abdur\OneDrive\Work\R-MCP\run_code_r.R"]
RUN_CODE_R_ENV = {}
TAVILY_CMD = "npx"
TAVILY_ARGS = ["-y", "tavily-mcp@latest"]
TAVILY_ENV = {"TAVILY_API_KEY": TAVILY_API_KEY}

LINKUP_CMD = "npx"
LINKUP_ARGS = ["-y", "linkup-mcp-server"]
LINKUP_ENV = {}

SEQUENTIAL_CMD = "npx"
SEQUENTIAL_ARGS = ["-y", "@modelcontextprotocol/server-sequential-thinking"]
SEQUENTIAL_ENV = {}

PDF2MD_CMD = "uv"
PDF2MD_ARGS = ["--directory", r"C:\Users\abdur\OneDrive\Work\mcp-pdf2md", "run", "pdf2md", "--output-dir", r"C:\Users\abdur\OneDrive\Work\compete-grok\inputs\pdfs"]
PDF2MD_ENV = {"MISTRAL_API_KEY": MISTRAL_API_KEY}

FILESYSTEM_CMD = "npx"
FILESYSTEM_ARGS = ["@modelcontextprotocol/server-filesystem", "-y", r"C:\Users\abdur\OneDrive\Work\compete-grok"]
FILESYSTEM_ENV = {}

if not XAI_API_KEY:
    print("Warning: XAI_API_KEY missing. Tools/LLMs will use mocks.")

LOG_LEVEL = 'DEBUG' if os.getenv('VERBOSE') else 'INFO'

# Maximum iterations for processing loops
MAX_ITERATIONS = 1

# Additional iteration and debate parameters
MAX_CURRENT_ITERATION = 5
HISTORY_THRESHOLD = 1
DEBATE_ROUND_LIMIT = 1