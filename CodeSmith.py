import streamlit as st
import os
from astra.agent import Agent
from astra.application import Application
from astra.llms import GeminiChat, OllamaLLM, OpenAIChat, AnthropicChat
from astra.task import Task
from astra.tools import PythonREPLTool, WriteFileTool, PistonExecuteTool, ExtractCodeBlockTool, ExtractTestCasesTool

# --- Streamlit Page Config ---
st.set_page_config(page_title="CodeSmith - Multi-Agent Codegen", layout="wide")
st.title("CodeSmith - Multi-Agent AI Code Generator")

# --- Sidebar Settings ---
st.sidebar.header("⚙️ Settings")

model_choice = st.sidebar.selectbox(
    "Choose Model Backend",
    ["Ollama (local)", "Gemini (cloud)", "OpenAI (cloud)", "Anthropic (cloud)"]
)

api_key = None
if model_choice == "Gemini (cloud)":
    api_key = st.sidebar.text_input("Gemini API Key", type="password")
elif model_choice == "OpenAI (cloud)":
    api_key = st.sidebar.text_input("OpenAI API Key", type="password")
elif model_choice == "Anthropic (cloud)":
    api_key = st.sidebar.text_input("Anthropic API Key", type="password")

# --- User Prompt ---
prompt = st.text_area(
    "💡 Enter your code generation request:",
    placeholder="e.g. Build a calculator CLI that reads from stdin and prints results (language of your choice)..."
)

run_button = st.button("🚀 Run Application")

"""Team roles tuned for a professional workflow"""
product_manager = Agent(
    name="Product Manager",
    role="Clarifies requirements, acceptance criteria, and concrete test cases",
    goal="Deliver precise scope and test cases the team must satisfy",
)

architect = Agent(
    name="Software Architect",
    role="Designs IO contract and structure so code is testable via stdin/stdout",
    goal="Eliminate interactivity; define clear input/output format",
)

developer = Agent(
    name="Developer",
    role="Implements the program according to the IO contract",
    goal="Produce correct, robust, and readable code",
)

qa_engineer = Agent(
    name="QA Engineer",
    role="Runs tests using Piston with provided stdin cases and reports results",
    goal="Accurately verify behavior across all cases",
)

fix_engineer = Agent(
    name="Tech Lead (Fixer)",
    role="Fixes failures identified by QA and re-tests",
    goal="Achieve all green tests with minimal changes",
)

doc_engineer = Agent(
    name="Documentation Engineer",
    role="Writes clear usage and examples based on the IO contract",
    goal="Provide concise docs aligned to the final solution",
)

# --- Run Application ---
if run_button and prompt:
    with st.spinner("Running agents..."):

        # --- Pick LLM backend ---
        if model_choice == "Ollama (local)":
            llm = OllamaLLM(model="qwen2.5-coder:7b")
        elif model_choice == "Gemini (cloud)":
            if not api_key:
                st.error("Please enter your Gemini API Key.")
                st.stop()
            llm = GeminiChat(
                model=os.environ.get("GEMINI_MODEL", "models/gemini-1.5-flash"),
                api_key=api_key,
            )
        elif model_choice == "OpenAI (cloud)":
            if not api_key:
                st.error("Please enter your OpenAI API Key.")
                st.stop()
            llm = OpenAIChat(
                model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
                api_key=api_key,
            )
        else:  # Anthropic
            if not api_key:
                st.error("Please enter your Anthropic API Key.")
                st.stop()
            llm = AnthropicChat(
                model=os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest"),
                api_key=api_key,
            )

        # --- Tasks ---
        requirements = Task(
            description=(
                f"You are planning the following request: {prompt}\n\n"
                "Deliver in this structure:\n"
                "- Acceptance Criteria (bullet points)\n"
                "- IO Contract: Specify exact stdin format and exact stdout format. Avoid interactive loops; all input must come from stdin.\n"
                "- Test Cases: Provide 4-6 cases as JSON with fields: name, stdin (single string with newlines), expected (exact stdout)."
            ),
            expected_output="Acceptance criteria, IO contract, and 4-6 concrete test cases with stdin and expected stdout.",
            agent=product_manager,
        )

        design = Task(
            description=(
        "Design the solution so it strictly follows the IO Contract above. "
        "Do not assume a specific language unless the user prompt mandates it. "
        "Outline the program structure and any helper functions."
            ),
            expected_output="Short design notes including function responsibilities and how stdin is parsed and stdout formatted.",
            agent=architect,
        )

        implementation = Task(
            description=(
                "Implement the program according to the IO Contract. Provide ONLY a single fenced code block with the complete program. "
                "The program must read from stdin as defined and print outputs exactly as expected. No menus, no prompts, no infinite loops."
            ),
            expected_output="A single code block containing the full solution.",
            agent=developer,
        )

        qa_test = Task(
            description=(
        "Use the code produced in the previous Developer step. "
        "First, use ExtractCodeBlockTool to obtain the latest fenced code and its language, and use ExtractTestCasesTool to parse the Product Manager's test cases list. "
        "Use the extractor's normalized_language (or language if normalized is null) as the 'language' for PistonExecuteTool. "
        "Run the program with PistonExecuteTool for EACH parsed test case. "
        "For each case: pass the test's stdin, capture stdout, and compare EXACTLY to expected. "
        "Do NOT spawn subprocesses within the test harness—run the program directly once per case. "
        "Return a compact JSON report listing each case with PASS/FAIL and actual stdout when failing."
            ),
            expected_output="A table-like summary of test results for all cases.",
            agent=qa_engineer,
        )

        fix_and_retest = Task(
            description=(
        "If any test failed, modify the code to fix issues. Provide the updated full code in a single fenced block, then rerun the tests with PistonExecuteTool and report results. "
                "If all passed already, reply with FINAL: All tests passed."
            ),
            expected_output="Either 'All tests passed' or updated code plus a second test report with all PASS.",
            agent=fix_engineer,
        )

        documentation = Task(
            description=(
                "Write concise usage docs based on the IO Contract and final behavior. Include 2 runnable examples showing stdin and expected stdout."
            ),
            expected_output="Short README-style usage with examples.",
            agent=doc_engineer,
        )

    # --- Build Application ---
        app = Application(
            agents=[product_manager, architect, developer, qa_engineer, fix_engineer, doc_engineer],
            tasks=[requirements, design, implementation, qa_test, fix_and_retest, documentation],
            tools=[PythonREPLTool, WriteFileTool, PistonExecuteTool, ExtractCodeBlockTool, ExtractTestCasesTool],
            llm=llm,
        )

        results = app.run()

        st.success("✅ Finished Running!")

        st.markdown("## Results by agent")
        sections = [
            (" Product Manager", product_manager, requirements),
            (" Architect", architect, design),
            (" Developer", developer, implementation),
            (" QA", qa_engineer, qa_test),
            (" Fix & Retest", fix_engineer, fix_and_retest),
            (" Documentation", doc_engineer, documentation),
        ]
        for title, agent_obj, task_obj in sections:
            with st.container(border=True):
                st.subheader(f"{title}")
                st.caption(f"Role: {agent_obj.role}")
                out = results.get(task_obj.description, "")
                if not out:
                    st.info("No output.")
                else:
                    st.markdown(out)

        # Optional raw debug
        with st.expander("🔍 Show raw results (debug)"):
            try:
                st.write(results)
            except Exception:
                st.text(str(results))
