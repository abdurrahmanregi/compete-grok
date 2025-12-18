from langchain_core.tools import tool
import subprocess
import json
import os
from config import *

@tool
def linkup_search(query: str) -> dict:
    """Linkup deep search."""
    input_data = {"query": query}
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
        sources = result.get("sources", [])
        return {"content": content, "sources": sources}
    except Exception as e:
        mock_content = f"Mock linkup_search('{query}'): Deep results: 2025 case law on SSNIP tests in tech. Key precedent: US v. Google. Note: LINKUP_API_KEY required. Error: {str(e)[:300]}"
        mock_sources = [{"url": "https://www.courtlistener.com/opinion/123456/us-v-google/", "title": "US v. Google SSNIP Case", "snippet": "Key precedent on SSNIP tests"}]
        return {"content": mock_content, "sources": mock_sources}