# CodeSmith – AI-Powered Code Generation Platform

CodeSmith is an intelligent coding assistant built on the **Astra** agentic AI framework. It simulates a software engineering team, where multiple specialized agents collaborate to generate, review, test, and document code across multiple programming languages.

---

## Features
- **Agentic multi-role workflow** – Agents coordinate like a real software engineering team.  
- **Multi-language support** – Support for Python, JavaScript, Java, C++, and more.  
- **Local LLM integration** – Runs with Ollama for offline model hosting; optional support for OpenAI and Gemini.  

---

##  Installation & Setup

Follow the steps below to set up the project:

```bash
# 1. Clone the repository
git clone https://github.com/sooryabyte/CodeSmith.git
cd codesmith

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install and configure Ollama (see https://ollama.ai)
# Example: pull a coding model (Qwen 2.5 Coder 7B)
ollama pull qwen2.5-coder:7b

# 5. Launch the Streamlit frontend
streamlit run CodeSmith.py

```
---

##  Usage

- Open the Streamlit URL (usually `http://localhost:8501`) shown in your terminal after launching.
- Enter a natural-language task (e.g., "Implement a REST endpoint in Flask that returns the sum of numbers") and submit.
- Run the application

---

##  Notes
- **Security & safety**: When running arbitrary generated code, use sandboxing where possible. The included Python REPL tool is convenient for demos but avoid running untrusted code on production hosts.
- **Extensibility**: Add new `Agent` roles by defining agent instances and hooking them into the workflow. Add language-specific test tools to support more languages.
- **Reproducibility**: Pin models and dependency versions in `requirements.txt` to ensure consistent behaviour across environments.

---
