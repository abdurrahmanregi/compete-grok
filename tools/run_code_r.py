from langchain_core.tools import tool
import subprocess
import json
import os
from config import *

@tool
def run_code_r(code: str) -> str:
    """Execute R code for quant tasks."""
    input_data = {"code": code}
    cmd = [RUN_CODE_R_CMD] + RUN_CODE_R_ARGS
    env = os.environ.copy()
    env.update(RUN_CODE_R_ENV)
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
        return f"Mock (MCP ready?): R HHI example: sum(sapply(c(0.4,0.3), function(s) s^2)) * 10000 = 2500. Note: Check env. Error: {str(e)[:300]}"