"""Run the benchmark query on both agents and save outputs to files."""
import sys
import subprocess
import os

BASE = os.path.dirname(os.path.abspath(__file__))
PYTHON_REACT = os.path.join(BASE, "ollama_react", ".venv", "Scripts", "python.exe")
PYTHON_PAOR = os.path.join(BASE, "ollama_react_planning", ".venv", "Scripts", "python.exe")

QUERY = (
    "Read sample.txt and find the formulas for a rectangle and a hollow circle. "
    "Calculate the moment of inertia for both: a rectangle 0.3 m x 0.5 m, and a "
    "hollow circle with outer diameter 0.5 m and inner diameter 0.45 m. Which "
    "cross-section has the higher moment of inertia per area? Search the web for "
    "the Young's modulus of titanium and calculate EI for the more efficient one."
)

RUNNER_CODE = '''
import sys, os
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
os.chdir(r"{cwd}")
sys.path.insert(0, r"{cwd}")
from agent import run_agent
run_agent("""{query}""")
'''

def run_one(label, python_exe, project_dir):
    print(f"\\n{'='*60}")
    print(f"  Running {label}...")
    print(f"{'='*60}")

    code = RUNNER_CODE.format(cwd=project_dir, query=QUERY)
    result = subprocess.run(
        [python_exe, "-c", code],
        capture_output=True, text=True, encoding="utf-8",
        timeout=600, cwd=project_dir
    )
    output = result.stdout
    if result.stderr:
        output += "\\n--- STDERR ---\\n" + result.stderr
    print(output)
    return output

if __name__ == "__main__":
    react_dir = os.path.join(BASE, "ollama_react")
    paor_dir = os.path.join(BASE, "ollama_react_planning")

    react_output = run_one("ReAct", PYTHON_REACT, react_dir)
    with open(os.path.join(BASE, "benchmark_react_output.txt"), "w", encoding="utf-8") as f:
        f.write(react_output)

    paor_output = run_one("PAOR", PYTHON_PAOR, paor_dir)
    with open(os.path.join(BASE, "benchmark_paor_output.txt"), "w", encoding="utf-8") as f:
        f.write(paor_output)

    print(f"\\n\\nDone! Outputs saved to benchmark_react_output.txt and benchmark_paor_output.txt")
