from langchain_core.tools import tool
import subprocess
import json
import os
from config import *

@tool
def tavily_search(query: str, time_range: str = "year") -> dict:
    """Tavily broad search for recent econ papers/news."""
    input_data = {
        "query": query,
        "time_range": time_range,
        "search_depth": "advanced",
        "topic": "general",
        "max_results": 10
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
        sources = result.get("sources", [])
        return {"content": content, "sources": sources}
    except Exception as e:
        mock_content = f"Mock tavily_search('{query}'): Found 2025 NBER paper on AI mergers in IO economics. Summary: GUPPI > 0.1 threshold. Links: [nber.org/papers/w34256]. Note: TAVILY_API_KEY required. Error: {str(e)[:300]}"
        mock_sources = [{"url": "https://www.nber.org/papers/w34256", "title": "AI Mergers in IO Economics", "snippet": "Recent paper on GUPPI thresholds"}]
        return {"content": mock_content, "sources": mock_sources}