import streamlit as st
import os
from astra.agent import Agent
from astra.application import Application
from astra.llms import GeminiChat, OllamaLLM
from astra.task import Task
from astra.tools import WriteFileTool, PythonREPLTool, ShellTool
import google.generativeai as genai

st.set_page_config(page_title="CodeSmith - Multi-Agent Codegen", layout="wide")

st.title("CodeSmith - AI Code Generator")

# --- Sidebar Settings ---
st.sidebar.header("⚙️ Settings")

model_choice = st.sidebar.selectbox(
    "Choose Model Backend",
    ["Ollama (local)", "Gemini (cloud)"]
)

api_key = None
if model_choice == "Gemini (cloud)":
    api_key = st.sidebar.text_input("Gemini API Key", type="password")

# --- User Prompt ---
prompt = st.text_area(
    "💡 Enter your code generation request:",
    placeholder="e.g. Generate a Python function that calculates factorial..."
)

run_button = st.button("Run Application")

# --- Define Agents ---
developer = Agent(
    name="Developer",
    role="Writes code for requested functionality in any language",
    goal="Generate correct and efficient code.",
)

executor = Agent(
    name="Executor",
    role="Executes code and reports results",
    goal="Run code safely and return outputs or errors.",
)

explainer = Agent(
    name="Explainer",
    role="Explains code and its functionality.",
    goal="Explain the code for better understanding of user.",
)

if run_button and prompt:
    with st.spinner("Running agents..."):

        # --- Pick LLM backend ---
        if model_choice == "Ollama (local)":
            llm = OllamaLLM(model="qwen2.5-coder:7b")
        else:
            if not api_key:
                st.error("Please enter your Gemini API Key.")
                st.stop()
            os.environ["GEMINI_API_KEY"] = api_key
            llm = GeminiChat(
                model=os.environ.get("GEMINI_MODEL", "models/gemini-1.5-flash"),
                api_key=api_key
            )
            genai.configure(api_key=api_key)

        # --- Define tasks dynamically from user prompt ---
        task1 = Task(
            description=prompt,
            expected_output="A complete and working code snippet.",
            agent=developer,
        )

        task2 = Task(
            description="Test the generated code by running it.",
            expected_output="Execution result of generated code.",
            agent=executor,
        )

        task3 = Task(
            description="Explain the working of the finished final code output.",
            expected_output="Explanation of generated code.",
            agent=explainer,
        )

        # --- Build Application ---
        app = Application(
            agents=[developer, executor, explainer],
            tasks=[task1, task2, task3],
            tools=[WriteFileTool, PythonREPLTool, ShellTool],
            llm=llm,
        )

        results = app.run()

        st.success("✅ Finished Running!")
        
        # Optional raw debug
        with st.expander("🔍 Show raw results (debug)"):
            try:
                st.write(results)
            except Exception:
                st.text(str(results))
