from langchain_core.tools import tool
import subprocess
import json
import os
from config import *
from compete_logging import get_logger

logger = get_logger(__name__)

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
        
        # Enhanced logging for auditing
        content = result.get("content", [])
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_val = item.get("text", "")
                    # Try to parse if it looks like JSON, otherwise log as text
                    try:
                        data = json.loads(text_val)
                        if isinstance(data, dict):
                            thought = data.get("thought")
                            hypothesis = data.get("hypothesis")
                            conclusion = data.get("conclusion")
                            if thought or hypothesis or conclusion:
                                logger.info(f"Sequential Thinking - Thought: {thought} | Hypothesis: {hypothesis} | Conclusion: {conclusion}")
                            else:
                                logger.info(f"Sequential Thinking Output: {text_val[:500]}...")
                        else:
                            logger.info(f"Sequential Thinking Output: {text_val[:500]}...")
                    except json.JSONDecodeError:
                        logger.info(f"Sequential Thinking Output: {text_val[:500]}...")
        else:
            logger.info(f"Sequential Thinking Result: {str(content)[:500]}...")

        return result.get("content", str(result))
    except Exception as e:
        error_msg = f"Mock sequential_thinking('{prompt[:50]}...'): Step 1: Hypothesis - market narrow. Step 2: SSNIP test. Step 3: Evidence from search. Reflection: Confirmed. Note: Check MCP. Error: {str(e)[:300]}"
        logger.error(f"Sequential thinking failed: {e}")
        return error_msg
