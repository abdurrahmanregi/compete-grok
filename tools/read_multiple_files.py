from langchain_core.tools import tool
import subprocess
import json
import os
from config import *

@tool
def read_multiple_files(paths: list[str]) -> dict:
    """Read multiple text files content."""
    input_data = {"paths": paths}
    cmd = [FILESYSTEM_CMD] + FILESYSTEM_ARGS
    env = os.environ.copy()
    env.update(FILESYSTEM_ENV)
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
        json_input = json.dumps(input_data)
        stdout, stderr = proc.communicate(input=json_input, timeout=180)
        proc.wait()
        if proc.returncode != 0:
            raise Exception(f"Return code {proc.returncode}: {stderr}")
        result = json.loads(stdout or "{}")
        return result if isinstance(result, dict) else {"error": str(result)}
    except Exception as e:
        return {"error": f"Error reading files {paths}: {str(e)}"}