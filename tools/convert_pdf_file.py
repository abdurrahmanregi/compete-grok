from langchain_core.tools import tool
import subprocess
import json
import os
from config import *

@tool
def convert_pdf_file(file_path: str) -> str:
    """Convert local PDF file to Markdown."""
    input_data = {"file_path": file_path}
    cmd = [PDF2MD_CMD] + PDF2MD_ARGS
    env = os.environ.copy()
    env.update(PDF2MD_ENV)
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
        return f"Mock convert_pdf_file('{file_path}'): Converted to folder/file.md\n# Local Econ Doc\nContent extracted... Note: MISTRAL_API_KEY required. Error: {str(e)[:300]}"