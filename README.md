CodeSmith
============

Overview
--------
CodeSmith is a multi‑agent code generation and evaluation system. It orchestrates specialized AI agents (Product Manager, Architect, Developer, QA, Fix / Tech Lead, Documentation) to translate a natural language software request into an implemented, tested, and documented program. The system supports multiple language model providers (local and cloud) and executes generated code safely through an online sandbox (Piston API) using stdin/stdout contracts for determinism.

Video Demonstration
-------------------
<img alt="Watch on YouTube" src="https://www.youtube.com/watch?v=ehxIGaaGq3E">
<video src="assets/CodeSmith.mp4" controls width="720"></video>

Key Features
------------
1. Multi‑agent pipeline with role separation (requirements → design → implementation → automated testing → fixes → documentation).
2. Provider abstraction layer supporting:
   - Ollama (local; e.g. qwen2.5-coder:7b or other locally pulled models)
   - Google Gemini
   - OpenAI Chat models
   - Anthropic Claude models
3. Language‑agnostic code generation (C, C++, Python, Java, Go, Rust, JavaScript/TypeScript, etc.)
4. Deterministic execution and automated QA through the public Piston API (no Docker required for default public endpoint).
5. Robust tool set:
   - PythonREPLTool: Quick in‑process Python evaluation for internal reasoning.
   - WriteFileTool: Persist artifacts to disk.
   - PistonExecuteTool: Remote compilation / execution with stdin support.
   - ExtractCodeBlockTool: Retrieves the latest fenced code block and normalizes language identifiers.
   - ExtractTestCasesTool: Parses structured test case arrays from prior agent output.
6. Test‑driven corrective loop: Failing cases trigger an automated fix cycle until all pass (or step limit reached).
7. Provider retry logic and graceful degradation (Gemini and Anthropic implementations include limited retry strategies).
8. Configuration via environment variables (override defaults without code changes).

Installation
------------
Requirements:
* Python 3.10+
* (Optional) Local Ollama installation if using Ollama provider.

1. Clone the repository:
```powershell
git clone https://github.com/sooryabyte/CodeSmith.git
cd CodeSmith
```
2. (Recommended) Create and activate a virtual environment:

Windows (PowerShell / venv):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux / macOS (bash / zsh, venv):
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Conda (cross‑platform):
```bash
conda create -n codesmith python=3.11 -y
conda activate codesmith
```
3. Install dependencies:
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```
4. (Optional) Pull or prepare an Ollama model:
```powershell
ollama pull qwen2.5-coder:7b
```

Configuration (Environment Variables)
-------------------------------------
| Variable              | Purpose | Default / Notes |
|-----------------------|---------|-----------------|
| `OPENAI_API_KEY`      | OpenAI provider authentication | Required for OpenAI mode |
| `GEMINI_API_KEY`      | Gemini provider authentication | Required for Gemini mode |
| `ANTHROPIC_API_KEY`   | Anthropic Claude authentication | Required for Anthropic mode |
| `OLLAMA_HOST`         | Ollama base URL | `http://localhost:11434` |
| `OPENAI_MODEL`        | Override OpenAI model ID | `gpt-4o-mini` |
| `GEMINI_MODEL`        | Override Gemini model ID | `models/gemini-1.5-flash` |
| `ANTHROPIC_MODEL`     | Override Anthropic model ID | `claude-3-5-sonnet-latest` |
| `PISTON_BASE_URL`     | Alternate Piston endpoint (self‑host) | Public endpoint if unset |

Usage
-----
Launch the primary Streamlit interface:
```powershell
streamlit run CodeSmith.py
```
Select a model backend (e.g. OpenAI, Gemini, Anthropic, Ollama), provide the corresponding API key if cloud‑based, enter a task (e.g. “Build a C++ CLI that reads 'op a b' lines and prints the numeric result”), and execute. Results are shown per agent in order. The final documentation includes example stdin invocations consistent with the acceptance criteria.

Security Considerations
-----------------------
* Code execution occurs remotely through Piston, reducing local risk.
* No shell tool is wired into the application UI (shell execution is intentionally excluded from production wiring).
* API keys are only read at runtime; avoid hard‑coding credentials.

Limitations
-----------
* Long outputs are not streamed progressively in the current Streamlit interface.
* QA loop iteration cap prevents infinite fix cycles (tune if necessary).
* Public Piston endpoint is rate‑limited; heavy usage may require self‑hosting.






