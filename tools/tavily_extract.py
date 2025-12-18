from langchain_core.tools import tool
import subprocess
import json
import os
from config import *

@tool
def tavily_extract(url: str) -> dict:
    """Tavily web content extraction."""
    input_data = {
        "urls": [url],
        "extract_depth": "advanced",
        "format": "markdown"
    }
    cmd = [TAVILY_CMD] + TAVILY_ARGS
    env = os.environ.copy()
    env.update(TAVILY_ENV)
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
        sources = result.get("sources", [{"url": url, "title": "Extracted Content", "snippet": content[:200]}])
        return {"content": content, "sources": sources}
    except Exception as e:
        mock_content = f"Mock tavily_extract('{url}'): Extracted markdown: # NBER Paper Title\nAbstract: Recent IO analysis... Note: TAVILY_API_KEY required. Error: {str(e)[:300]}"
        mock_sources = [{"url": url, "title": "Mock Extracted Title", "snippet": "Mock snippet from extraction"}]
        return {"content": mock_content, "sources": mock_sources}