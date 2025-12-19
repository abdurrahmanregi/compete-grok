import argparse
import os
import subprocess
from datetime import datetime
from pathlib import Path
from langchain_core.messages import HumanMessage, AIMessage
from graph import create_workflow  # function to create graph
from tools.convert_pdf_file import convert_pdf_file  # for uploads
import re
import textwrap
import logging
import json

from dotenv import load_dotenv; load_dotenv()
from agents.agents import agents

def fix_md_math(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip('\n')
        if re.match(r'^\s*(?:\\\[|$$)', line):
            # Start of math block
            block = [line]
            i += 1
            while i < len(lines) and not re.match(r'^\s*(?:\\]|$$)', lines[i].rstrip('\n')):
                block.append(lines[i].rstrip('\n'))
                i += 1
            if i < len(lines):
                block.append(lines[i].rstrip('\n'))
                i += 1
            # Dedent block
            block_text = '\n'.join(block) + '\n'
            dedented = textwrap.dedent(block_text)
            fixed_lines.extend(dedented.splitlines(keepends=True))
        else:
            fixed_lines.append(lines[i])
            i += 1
    
    fixed_content = ''.join(fixed_lines)
    fixed_path = md_path.replace('.md', '_fixed.md')
    with open(fixed_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    return fixed_path
 

parser = argparse.ArgumentParser(description="CompeteGrok: IO Economics AI")
parser.add_argument("--query", type=str, required=True, help="Query text or path to .txt file (multi-line)")
parser.add_argument("--file", type=str, nargs="*", help="PDF/Excel uploads for RAG")
parser.add_argument("--verbose", action="store_true", help="Verbose output")
parser.add_argument("--output-dir", type=str, default="./outputs", help="Output dir")
parser.add_argument("--debate", action="store_true", help="Force debate module regardless of supervisor routing")
args = parser.parse_args()

logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
logger = logging.getLogger(__name__)

if args.query.endswith('.txt'):
    query_path = Path(args.query)
    if query_path.exists():
        content = query_path.read_text(encoding="utf-8").strip()
        if content.startswith('"""') and content.endswith('"""'):
            content = content[3:-3].strip()
        lines = content.splitlines()
        query_text = ""
        file_paths = []
        in_query = False
        in_files = False
        for line in lines:
            line = line.strip()
            if line.upper() == "QUERY:":
                in_query = True
                in_files = False
                continue
            elif line.upper() == "FILES:":
                in_files = True
                in_query = False
                continue
            if in_query:
                query_text += line + "\n"
            elif in_files and line:
                file_paths.append(line)
        if not query_text.strip():
            query_text = content
        args.query = query_text.strip()
        if file_paths:
            if args.file is None:
                args.file = file_paths
            else:
                args.file.extend(file_paths)
        if args.verbose:
            print(f"Loaded and parsed query from file: {query_path}")
    else:
        raise ValueError(f"Query file not found: {args.query}")

# Run TeamFormationAgent to select agents
logger.info("Running TeamFormationAgent...")
team_result = agents["teamformation"].invoke({"messages": [HumanMessage(content=args.query)]})
selected_agents = json.loads(team_result["messages"][-1].content)
logger.info(f"Selected agents: {selected_agents}")

# Create workflow with selected agents
workflow = create_workflow(selected_agents)

output_dir = Path(args.output_dir)
output_dir.mkdir(exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

state = {
    "messages": [HumanMessage(content=f"{args.query}\n\nForce debate: {args.debate}")],
    "documents": [],
    "routes": [],
    "final_synthesis": "",
    "iteration_count": 0,
    "routing_history": [],
    "force_debate": args.debate,
    "sources": [],
    "debate_round": 0,
    "debate_count": 0,
}

if args.file:
    for file_path in args.file:
        if args.verbose: print(f"Processing upload: {file_path}")
        try:
            md_content = convert_pdf_file(file_path)
            state["documents"].append(md_content)
        except Exception as e:
            logger.warning(f"Upload error: {e}")

logger.info("Invoking workflow...")
try:
    result = workflow.invoke(state)
    logger.info("Workflow complete")
except Exception as e:
    logger.error(f"Workflow invoke error: {e}")
    result = {
        "messages": state["messages"] + [AIMessage(content=f"**Error:** {str(e)}\nReflected: See caveats.")],
        "final_synthesis": f"Error occurred: {e}. Reflection: Check logs/caveats.",
        "routes": getattr(state, "routes", [])
    }

if args.verbose:
    logger.debug(f"Workflow result: {result}")

# Extract report: final_synthesis
report_content = "# CompeteGrok Analysis Report\n\n"
report_content += f"**Query:** {args.query}\n\n"
report_content += f"**Selected Agents:** {selected_agents}\n\n"
report_content += f"**Timestamp:** {datetime.now()}\n\n"
report_content += f"**Routes:** {result.get('routes', 'N/A')}\n\n"
final_synth = result.get("final_synthesis")
if not final_synth:
    # Use the last AIMessage content if no final_synthesis
    messages = result.get("messages", [])
    for msg in reversed(messages):
        if hasattr(msg, 'content') and msg.content.strip():
            final_synth = msg.content
            break
report_content += (final_synth or "No synthesis available.") + "\n\n"

# Append References
sources = result.get("sources", [])
if sources:
    report_content += "### References\n"
    for i, source in enumerate(sources, 1):
        title = source.get("title", "Unknown Title")
        url = source.get("url", "Unknown URL")
        report_content += f"{i}. {title} - {url}\n"
    report_content += "\n"

report_content += """
**Privacy:** Ephemeral RAG; zero retention.
**Disclaimer:** Not legal advice. Models have caveats (e.g. IIA assumption). Verify 2025 data.
**LaTeX:** Inline $x$, display $$E=mc^2$$.
"""

md_path = output_dir / f"report_{timestamp}.md"
with open(md_path, "w", encoding="utf-8") as f:
    f.write(report_content)

try:
    fixed_md_path = fix_md_math(str(md_path))
except Exception as e:
    logger.warning(f"MD preprocess failed: {e}. Using original MD.")
    fixed_md_path = str(md_path)

pdf_path = md_path.with_suffix(".pdf")
try:
    subprocess.run([
        "pandoc", fixed_md_path, "-o", str(pdf_path),
        "-f", "markdown+tex_math_dollars+tex_math_single_backslash+tex_math_double_backslash",
        "--pdf-engine=xelatex",
        "--variable", "header-includes:\\usepackage{amsmath}\\usepackage{amssymb}\\usepackage{geometry}\\geometry{margin=1in}",
        "--variable", "fontsize=11pt",
        "--variable", "mainfont=Arial",  # LaTeX compat
    ], check=True, capture_output=True)
    logger.info(f"✅ Generated:\n{md_path}\n{pdf_path}")
except subprocess.CalledProcessError as e:
    stderr_msg = e.stderr.decode('utf-8', errors='ignore') if e.stderr else str(e)
    logger.error(f"❌ PDF failed: {stderr_msg}. MD ready: {md_path}")
except FileNotFoundError:
    logger.error(f"❌ Pandoc not found. Install: https://pandoc.org/. MD: {md_path}")

if args.verbose:
    logger.info("Done.")