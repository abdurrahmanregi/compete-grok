from dotenv import load_dotenv
import os
load_dotenv()

# Import custom logging and exceptions
from compete_logging import setup_logging, get_logger
from exceptions import ConfigurationError

# API Keys
XAI_API_KEY = os.getenv('XAI_API_KEY')
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
LINKUP_API_KEY = os.getenv('LINKUP_API_KEY')
LANGCHAIN_API_KEY = os.getenv('LANGCHAIN_API_KEY')
LANGCHAIN_TRACING_V2 = os.getenv('LANGCHAIN_TRACING_V2')
LANGCHAIN_PROJECT = os.getenv('LANGCHAIN_PROJECT')
VERBOSE = os.getenv('VERBOSE')

# Validate API keys
if not XAI_API_KEY:
    print("Warning: XAI_API_KEY not set. Using mock models.")
if not TAVILY_API_KEY:
    print("Warning: TAVILY_API_KEY not set. Tavily tools may fail.")
if not MISTRAL_API_KEY:
    print("Warning: MISTRAL_API_KEY not set. PDF conversion may fail.")
if not LINKUP_API_KEY:
    print("Warning: LINKUP_API_KEY not set. Linkup tools may fail.")

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
DEBATE_CONS_MODEL = "grok-4-1-fast-reasoning"
DEBATE_ARBITER_MODEL = "grok-4-1-fast-non-reasoning"
TEAMFORMATION_MODEL = "grok-4-1-fast-reasoning"
VERIFIER_MODEL = "grok-4-1-fast-reasoning"

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
TAVILY_ARGS = ["@modelcontextprotocol/server-tavily-search"]
TAVILY_ENV = {"TAVILY_API_KEY": TAVILY_API_KEY}
TAVILY_MAX_RESULTS = 5

LINKUP_CMD = "npx"
LINKUP_ARGS = ["-y", "linkup-mcp-server"]
LINKUP_ENV = {}

SEQUENTIAL_CMD = "npx"
SEQUENTIAL_ARGS = ["-y", "@modelcontextprotocol/server-sequential-thinking"]
SEQUENTIAL_ENV = {}


FILESYSTEM_CMD = "npx"
FILESYSTEM_ARGS = ["@modelcontextprotocol/server-filesystem", "-y", r"C:\Users\abdur\OneDrive\Work\compete-grok"]
FILESYSTEM_ENV = {}

if not XAI_API_KEY:
    print("Warning: XAI_API_KEY missing. Tools/LLMs will use mocks.")

LOG_LEVEL = 'DEBUG' if os.getenv('VERBOSE') else 'INFO'

# Initialize logging
# Moved to app.py to avoid side effects on import
# try:
#     log_file = os.getenv('LOG_FILE', 'logs/compete_grok.log')
#     setup_logging(LOG_LEVEL, log_file)
#     logger = get_logger(__name__)
#     logger.info("Logging initialized successfully")
# except Exception as e:
#     print(f"Failed to initialize logging: {e}")
#     raise ConfigurationError(f"Logging setup failed: {e}")

# Maximum iterations for processing loops
MAX_ITERATIONS = 2

# Strict Mode: If True, tools raise exceptions instead of returning mocks.
STRICT_MODE = True

# Additional iteration and debate parameters
MAX_CURRENT_ITERATION = 8
HISTORY_THRESHOLD = 1
DEBATE_ROUND_LIMIT = 2