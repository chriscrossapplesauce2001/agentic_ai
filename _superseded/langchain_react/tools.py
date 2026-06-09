import os
import math
import numexpr
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchResults

# --- Tool 1: Web Search (returns snippets + source URLs) ---
search_tool = DuckDuckGoSearchResults(
    name="web_search",
    description="Search the web for current information. Input should be a search query string. Returns snippets with source URLs.",
)

# --- Tool 2: Calculator ---
@tool
def calculator(expression: str) -> str:
    """Calculate a math expression. Input must be a valid math expression like '2 + 2' or '(3.14 * 0.2 * 0.4**3) / 12'. Supports +, -, *, /, **, sqrt, sin, cos, log, pi, e."""
    try:
        local_dict = {"pi": math.pi, "e": math.e}
        result = numexpr.evaluate(expression.strip(), global_dict={}, local_dict=local_dict)
        return f"Result: {float(result)}"
    except Exception as exc:
        return f"Error evaluating '{expression}': {exc}"

# --- Tool 3: File Reader ---
ALLOWED_DIR = os.path.dirname(os.path.abspath(__file__))

@tool
def read_file(filename: str) -> str:
    """Read a local text file. Input should be a filename like 'sample.txt'. Only files in the project directory can be read."""
    safe_name = os.path.basename(filename)
    filepath = os.path.join(ALLOWED_DIR, safe_name)
    if not os.path.isfile(filepath):
        return f"Error: File '{safe_name}' not found in project directory."
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read(10_000)
        return content
    except Exception as exc:
        return f"Error reading '{safe_name}': {exc}"

# All tools in one list for easy import
tools = [search_tool, calculator, read_file]
