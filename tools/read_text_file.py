from langchain_core.tools import tool
import subprocess
import json
import os
from config import *

@tool
def read_text_file(path: str) -> str:
    """Read text file content."""
    input_data = {"path": path}
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
        return result.get("content", str(result))
    except Exception as e:
        return f"Error reading file '{path}': {str(e)}"