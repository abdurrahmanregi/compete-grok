"""CompeteGrok CLI Application.

This module provides the command-line interface for running CompeteGrok,
an AI-powered system for antitrust analysis. It handles query processing,
agent orchestration, and report generation.
"""

import argparse
import os
import subprocess
import shlex
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
from agents import agents
from exceptions import WorkflowError, AgentError, FileProcessingError

def fix_md_math(md_path: str) -> str:
    """Fixes LaTeX math block indentation in Markdown files for Pandoc compatibility.

    Processes the input Markdown file to dedent LaTeX math blocks (delimited by
    \\[ ... \\] or $$ ... $$) that may have been indented, which can cause Pandoc
    to fail rendering them as math. Creates a new file with '_fixed' suffix.

    Args:
        md_path (str): Path to the input Markdown file.

    Returns:
        str: Path to the fixed Markdown file with dedented math blocks.

    Raises:
        FileNotFoundError: If the input file does not exist.
        IOError: If there are issues reading from or writing to files.
    """
    # Read the input Markdown file
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    fixed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip('\n')
        # Check for start of LaTeX math block (either \[ or $$ with optional leading whitespace)
        if re.match(r'^\s*(?:\\\[|$$)', line):
            # Start of math block
            block = [line]
            i += 1
            # Collect all lines until the end of the math block
            while i < len(lines) and not re.match(r'^\s*(?:\\]|$$)', lines[i].rstrip('\n')):
                block.append(lines[i].rstrip('\n'))
                i += 1
            if i < len(lines):
                block.append(lines[i].rstrip('\n'))
                i += 1
            # Dedent the entire block to remove any common leading whitespace
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
 

# Set up command-line argument parser
parser = argparse.ArgumentParser(description="CompeteGrok: IO Economics AI")
parser.add_argument("--query", type=str, required=True, help="Query text or path to .txt file (multi-line)")
parser.add_argument("--file", type=str, nargs="*", help="PDF/Excel uploads for RAG")
parser.add_argument("--verbose", action="store_true", help="Verbose output")
parser.add_argument("--log-level", type=str, default=None, choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Set logging level")
parser.add_argument("--output-dir", type=str, default="./outputs", help="Output dir")
parser.add_argument("--debate", action="store_true", help="Force debate module regardless of supervisor routing")
args = parser.parse_args()

# Validate user inputs
if not args.query or not args.query.strip():
    parser.error("Query cannot be empty.")

if args.file:
    for file_path in args.file:
        if not os.path.isfile(file_path):
            parser.error(f"File does not exist: {file_path}")

if not os.path.isdir(args.output_dir):
    try:
        os.makedirs(args.output_dir, exist_ok=True)
    except OSError as e:
        parser.error(f"Cannot create output directory: {e}")

# Configure logging based on arguments
log_level = getattr(logging, args.log_level or ('DEBUG' if args.verbose else 'INFO'))
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)

# If query argument ends with .txt, treat it as a file path and parse it
if args.query.endswith('.txt'):
    query_path = Path(args.query)
    if query_path.exists():
        # Read the entire file content and strip whitespace
        content = query_path.read_text(encoding="utf-8").strip()
        # Remove surrounding triple quotes if present (for multi-line strings)
        if content.startswith('"""') and content.endswith('"""'):
            content = content[3:-3].strip()
        # Split content into lines for section-based parsing
        lines = content.splitlines()
        query_text = ""
        file_paths = []
        in_query = False
        in_files = False
        # Parse lines to extract QUERY and FILES sections
        for line in lines:
            line = line.strip()
            # Start of QUERY section
            if line.upper() == "QUERY:":
                in_query = True
                in_files = False
                continue
            # Start of FILES section
            elif line.upper() == "FILES:":
                in_files = True
                in_query = False
                continue
            # Append to query text if in QUERY section
            if in_query:
                query_text += line + "\n"
            # Append to file paths if in FILES section and line is not empty
            elif in_files and line:
                file_paths.append(line)
        # If no QUERY section found, use entire content as query
        if not query_text.strip():
            query_text = content
        # Update args.query with parsed query text
        args.query = query_text.strip()
        # Update args.file with parsed file paths if any
        if file_paths:
            if args.file is None:
                args.file = file_paths
            else:
                args.file.extend(file_paths)
        # Log the file loading if verbose mode
        if args.verbose:
            print(f"Loaded and parsed query from file: {query_path}")
    else:
        raise ValueError(f"Query file not found: {args.query}")

# Run TeamFormationAgent to select agents based on query
logger.info("Running TeamFormationAgent...")
try:
    team_result = agents["teamformation"].invoke({"messages": [HumanMessage(content=f"{args.query}\n\nForce debate: {args.debate}")]})
    selected_agents = json.loads(team_result["messages"][-1].content)
    logger.info("Selected agents: %s", selected_agents)
except json.JSONDecodeError as e:
    logger.error("Failed to parse teamformation output: %s", str(e), exc_info=True)
    raise AgentError(f"TeamFormation agent output parsing failed: {e}") from e
except Exception as e:
    logger.error("Error in TeamFormationAgent: %s", str(e), exc_info=True)
    raise AgentError(f"TeamFormation agent failed: {e}") from e

# Create workflow with selected agents
try:
    workflow = create_workflow(selected_agents)
except WorkflowError as e:
    logger.error("Workflow creation failed: %s", str(e), exc_info=True)
    raise
except Exception as e:
    logger.error("Unexpected error creating workflow: %s", str(e), exc_info=True)
    raise WorkflowError(f"Unexpected workflow creation error: {e}") from e

# Prepare output directory and timestamp
output_dir = Path(args.output_dir)
output_dir.mkdir(exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Initialize state dictionary for workflow
state = {
    "messages": [HumanMessage(content=f"{args.query}\n\nSelected agents: {json.dumps(selected_agents)}\n\nForce debate: {args.debate}")],
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

# Process uploaded files if provided
if args.file:
    for file_path in args.file:
        if args.verbose: print(f"Processing upload: {file_path}")
        try:
            md_content = convert_pdf_file(file_path)
            if md_content.startswith(("File not found", "Invalid PDF", "OCR error")):
                logger.warning(f"Upload processing failed: {md_content}")
            else:
                state["documents"].append(md_content)
                logger.info(f"Successfully processed upload: {file_path}")
        except (OSError, ValueError) as e:
            logger.warning(f"Upload error: {e}")

# Invoke the workflow with the prepared state
logger.info("Invoking workflow...")
try:
    # raise ValueError("Simulated workflow error")  # Uncomment to test
    result = workflow.invoke(state)
    logger.info("Workflow invoked successfully")
except (ValueError, KeyError, RuntimeError, TypeError) as e:
    logger.error(f"Workflow invoke error: {e}")
    result = {
        "messages": state["messages"] + [AIMessage(content=f"**Error:** {str(e)}\nReflected: See caveats.")],
        "final_synthesis": f"Error occurred: {e}. Reflection: Check logs/caveats.",
        "routes": getattr(state, "routes", [])
    }
except Exception as e:
    logger.error(f"Unexpected workflow invoke error: {e}")
    result = {
        "messages": state["messages"] + [AIMessage(content=f"**Unexpected Error:** {str(e)}\nReflected: See caveats.")],
        "final_synthesis": f"Unexpected error occurred: {e}. Reflection: Check logs/caveats.",
        "routes": getattr(state, "routes", [])
    }

if args.verbose:
    logger.debug(f"Workflow result: {result}")

# Generate the report content in Markdown format
report_content = "# CompeteGrok Analysis Report\n\n"
report_content += f"**Query:** {args.query}\n\n"
report_content += f"**Selected Agents:** {selected_agents}\n\n"
report_content += f"**Timestamp:** {datetime.now()}\n\n"
report_content += f"**Routes:** {result.get('routes', 'N/A')}\n\n"
# Retrieve final synthesis from result, fallback to last message content if not present
final_synth = result.get("final_synthesis")
if not final_synth:
    # Use the last AIMessage content if no final_synthesis
    messages = result.get("messages", [])
    for msg in reversed(messages):
        if hasattr(msg, 'content') and msg.content.strip():
            final_synth = msg.content
            break
report_content += (final_synth or "No synthesis available.") + "\n\n"

# Append References section if sources are available
sources = result.get("sources", [])
if sources:
    report_content += "### References\n"
    for i, source in enumerate(sources, 1):
        title = source.get("title", "Unknown Title")
        url = source.get("url", "Unknown URL")
        report_content += f"{i}. {title} - {url}\n"
    report_content += "\n"

# report_content += """
# **Privacy:** Ephemeral RAG; zero retention.
# **Disclaimer:** Not legal advice. Models have caveats (e.g. IIA assumption). Verify 2025 data.
# **LaTeX:** Inline $x$, display $$E=mc^2$$.
# """

# Write the report to Markdown file
md_path = output_dir / f"report_{timestamp}.md"
try:
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    logger.info("Report written to %s", md_path)
except (OSError, IOError) as e:
    logger.error("Failed to write report to %s: %s", md_path, str(e), exc_info=True)
    raise FileProcessingError(f"Report writing failed: {e}") from e

# Fix LaTeX math blocks for Pandoc compatibility
try:
    fixed_md_path = fix_md_math(str(md_path))
    logger.info(f"MD math fixed successfully: {fixed_md_path}")
except (FileNotFoundError, OSError) as e:
    logger.warning(f"MD preprocess failed: {e}. Using original MD.")
    fixed_md_path = str(md_path)
except Exception as e:
    logger.warning(f"Unexpected MD preprocess error: {e}. Using original MD.")
    fixed_md_path = str(md_path)

# Ensure paths use forward slashes for pandoc compatibility
fixed_md_path = fixed_md_path.replace('\\', '/')
pdf_path = str(md_path.with_suffix(".pdf")).replace('\\', '/')

# Convert the fixed Markdown to PDF using Pandoc with XeLaTeX engine for math rendering
try:
    subprocess.run([
        "pandoc", fixed_md_path, "-o", pdf_path,
        "-f", "markdown+tex_math_dollars+tex_math_single_backslash+tex_math_double_backslash",
        "--pdf-engine=xelatex",
        "--variable", "header-includes:\\usepackage{amsmath}\\usepackage{amssymb}\\usepackage{geometry}\\geometry{margin=1in}",
        "--variable", "fontsize=11pt",
        "--variable", "mainfont=Arial",  # LaTeX compat
    ], check=True, capture_output=True)
    logger.info(f"PDF generated successfully: {pdf_path}")
except subprocess.CalledProcessError as e:
    stderr_msg = e.stderr.decode('utf-8', errors='ignore') if e.stderr else str(e)
    logger.error(f"PDF generation failed: {stderr_msg}. MD available: {md_path}")
except FileNotFoundError:
    logger.error(f"Pandoc not found. Install from https://pandoc.org/. MD available: {md_path}")

if args.verbose:
    logger.info("Done.")