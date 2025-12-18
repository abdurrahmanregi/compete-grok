from langchain_core.tools import tool
import subprocess
import json
import os
from config import *

@tool
def linkup_fetch(url: str) -> dict:
    """Linkup fetch content from URL."""
    input_data = {"urls": [url]}
    cmd = [LINKUP_CMD] + LINKUP_ARGS
    if LINKUP_API_KEY:
        cmd += [f"apiKey={LINKUP_API_KEY}"]
    env = os.environ.copy()
    env.update(LINKUP_ENV)
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
        content = result.get("content", str(result))
        sources = result.get("sources", [{"url": url, "title": "Fetched Content", "snippet": content[:200]}])
        return {"content": content, "sources": sources}
    except Exception as e:
        mock_content = f"Mock linkup_fetch('{url}'): Fetched: Detailed case summary from courtlistener.com... Note: LINKUP_API_KEY required. Error: {str(e)[:300]}"
        mock_sources = [{"url": url, "title": "Mock Fetched Title", "snippet": "Mock snippet from fetch"}]
        return {"content": mock_content, "sources": mock_sources}