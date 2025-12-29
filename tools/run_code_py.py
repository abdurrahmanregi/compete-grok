from langchain_core.tools import tool
import subprocess
import json
import os
import logging
from config import *

logger = logging.getLogger(__name__)

@tool
def run_code_py(code: str) -> str:
    """Execute Python code for quant tasks."""
    input_data = {"code": code}
    cmd = [RUN_CODE_PY_CMD] + RUN_CODE_PY_ARGS
    env = os.environ.copy()
    env.update(RUN_CODE_PY_ENV)
    try:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True,
            encoding='utf-8'
        )
        json_input = json.dumps({"input": input_data})
        stdout, stderr = proc.communicate(input=json_input, timeout=180)
        proc.wait()
        if proc.returncode != 0:
            raise Exception(f"Return code {proc.returncode}: {stderr}")
        result = json.loads(stdout or "{}")
        return result.get("result", result.get("content", str(result)))
    except Exception as e:
        logger.error(f"Error in run_code_py: {e}")  # Log subprocess or execution errors for debugging
        return f"Mock (MCP ready?): HHI example: {sum(s**2 for s in [0.4, 0.3]) * 10000:.0f}. Note: Check env. Error: {str(e)[:300]}"