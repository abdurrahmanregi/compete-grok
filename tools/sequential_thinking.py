from langchain_core.tools import tool
import subprocess
import json
import os
from config import *

@tool
def sequential_thinking(prompt: str) -> str:
    """Sequential thinking for hypothesis testing."""
    input_data = {"prompt": prompt}
    cmd = [SEQUENTIAL_CMD] + SEQUENTIAL_ARGS
    env = os.environ.copy()
    env.update(SEQUENTIAL_ENV)
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
        return result.get("content", str(result))
    except Exception as e:
        return f"Mock sequential_thinking('{prompt[:50]}...'): Step 1: Hypothesis - market narrow. Step 2: SSNIP test. Step 3: Evidence from search. Reflection: Confirmed. Note: Check MCP. Error: {str(e)[:300]}"