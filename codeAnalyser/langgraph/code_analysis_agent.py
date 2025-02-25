import os
from typing import Annotated, TypedDict
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langgraph.graph import StateGraph, END
import streamlit

# Load environment variables from .env file
load_dotenv()

# Define configuration variables for the Azure OpenAI API
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
key = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_GPT4_DEPLOYMENT_NAME = os.getenv("AZURE_GPT4_DEPLOYMENT_NAME")

# Initialize an instance of AzureChatOpenAI with the specified parameters
llm = AzureChatOpenAI(
    temperature=0.1,
    model=AZURE_GPT4_DEPLOYMENT_NAME,
    azure_endpoint=endpoint,
    openai_api_key=key,
    api_version=AZURE_OPENAI_API_VERSION
)

# Define a TypedDict for the analysis state
class AnalysisState(TypedDict):
    file_tree: str
    file_contents: str
    programming_language: str
    analysis_result: str
    iteration: int
    human : str

import os
from typing import Annotated, TypedDict
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langgraph.graph import StateGraph, END

# Load environment variables from .env file
load_dotenv()

# Define configuration variables for the Azure OpenAI API
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
key = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_GPT4_DEPLOYMENT_NAME = os.getenv("AZURE_GPT4_DEPLOYMENT_NAME")

# Initialize an instance of AzureChatOpenAI with the specified parameters
llm = AzureChatOpenAI(
    temperature=0.1,
    model=AZURE_GPT4_DEPLOYMENT_NAME,
    azure_endpoint=endpoint,
    openai_api_key=key,
    api_version=AZURE_OPENAI_API_VERSION
)

# Define a TypedDict for the analysis state
class AnalysisState(TypedDict):
    file_tree: str
    file_contents: str
    programming_language: str
    analysis_result: str
    iteration: int
    human_input : str

# --- Human Input Function ---
def get_human_input(state: AnalysisState) -> AnalysisState:
    """Collects human input for the review agent."""
    print("\nPlease review the repository details and provide any additional comments or instructions.")
    human_input = input("Enter your comments or instructions: ")
    state["human_input"] = human_input
    return state


# Define the prompt template for code analysis
PROMPT_TEMPLATE = """
You are Code Analyzer Agent (CAA), an expert AI code analyst. Your task is to analyze the provided code for potential issues based on the following instructions and guidelines.
{human_input}
**Input:**

*   **Code:**
    ```
    {code}
    ```
*   **Programming Language:** {language}
*   **Analysis Focus:** {analysis_focus} (e.g., security vulnerabilities, performance bottlenecks, code style, maintainability, specific bug patterns).
*   **Style Guide (Optional):** {style_guide} (e.g., PEP 8 for Python, Google Style Guide for Java). If no style guide is provided, use best practices for the given language.
*   **Specific Instructions:** {specific_instructions} (e.g., "Focus specifically on potential SQL injection vulnerabilities", "Check if error handling is implemented correctly", "Check for resource leaks")

**Guardrails:**

*   **Security:**
    *   DO NOT expose any PII, secrets, API keys, passwords, or confidential data. Redact them immediately.
    *   DO NOT execute the provided code.
    *   Avoid suggesting dangerous operations that could introduce security vulnerabilities.
*   **Factuality & Accuracy:**
    *   All reported issues MUST be backed by evidence from the code (cite line numbers).
    *   Avoid speculation. If you are unsure, state your uncertainty.
    *   Stay within the specified scope.
*   **Ethics & Bias:**
    *   Use neutral and objective language.
    *   Avoid biases related to coding style, language preference, or coding patterns.
*   **Output Format:**
    *   Use a structured Markdown format for the analysis.
    *   Be concise and actionable.
    *   Prioritize high-severity issues.

**Output Format (Markdown):**

```markdown
## Code Analysis Report

### Summary

[Brief overview of the analysis results.  Mention number of high/medium/low severity issues found.]

### High Severity Issues

[List issues that pose significant risks, such as security vulnerabilities or critical errors.  For each issue:]

*   **Issue:** [Brief description of the issue]
*   **Severity:** High
*   **Location:** [File name and line number(s)]
*   **Code Snippet:**
    ```[language]
    [Relevant code snippet]
    ```
*   **Explanation:** [Detailed explanation of the issue and why it is problematic]
*   **Recommendation:** [Specific steps to fix the issue]

### Medium Severity Issues

[List issues that could lead to errors, performance problems, or maintainability issues. Follow the same format as above.]

*   **Issue:** ...
*   **Severity:** Medium
*   **Location:** ...
*   **Code Snippet:** ...
*   **Explanation:** ...
*   **Recommendation:** ...

### Low Severity Issues

[List minor issues, such as style violations or minor inefficiencies. Follow the same format as above.]

*   **Issue:** ...
*   **Severity:** Low
*   *   **Location:** ...
*   **Code Snippet:** ...
*   **Explanation:** ...
*   **Recommendation:** ...

### Conclusion

[Concluding remarks summarizing the overall code quality and highlighting key areas for improvement.]
"""

# Function to analyze code
def analyze_code(state: AnalysisState):
    # Create the analysis prompt using the template
    analysis_prompt = PROMPT_TEMPLATE.format(
        code=state['file_contents'],
        language=state['programming_language'],
        human_input=state['human_input'],
        analysis_focus="security vulnerabilities, performance bottlenecks, code style, maintainability",
        style_guide="PEP 8" if state['programming_language'] == "Python" else "",
        specific_instructions="Focus specifically on potential SQL injection vulnerabilities, check if error handling is implemented correctly, check for resource leaks"
    )
    # Invoke the model with the analysis prompt
    response = llm.invoke([{"role": "system", "content": analysis_prompt}])
    return {"analysis_result": response.content, "iteration": state["iteration"] + 1}

# Function to reflect on the analysis
def reflect_on_analysis(state: AnalysisState):
    # Create the reflection prompt using the template
    reflection_prompt = PROMPT_TEMPLATE.format(
        code=state['file_contents'],
        language=state['programming_language'],
        human_input=state['human_input'],
        analysis_focus="security vulnerabilities, performance bottlenecks, code style, maintainability",
        style_guide="PEP 8" if state['programming_language'] == "Python" else "",
        specific_instructions="Focus specifically on potential SQL injection vulnerabilities, check if error handling is implemented correctly, check for resource leaks"
    )
    # Invoke the model with the reflection prompt
    response = llm.invoke([{"role": "system", "content": reflection_prompt}])
    return {"analysis_result": response.content, "iteration": state["iteration"] + 1}

# Function to determine if the analysis should continue
def should_continue(state: AnalysisState):
    # Continue if the iteration count is less than 3
    if state["iteration"] >= 3:
        return END
    return "reflect_on_analysis"

# Initialize the state graph
graph_builder = StateGraph(AnalysisState)
graph_builder.add_node("get_human_input", get_human_input)
graph_builder.add_node("analyze_code", analyze_code)
graph_builder.add_node("reflect_on_analysis", reflect_on_analysis)

# Set the entry point
graph_builder.set_entry_point("get_human_input")

# Add conditional edges
graph_builder.add_conditional_edges(
    "reflect_on_analysis",
    should_continue,
    {END: END, "reflect_on_analysis": "reflect_on_analysis"},
)

# Add edges
graph_builder.add_edge("get_human_input", "analyze_code")
graph_builder.add_edge("analyze_code", "reflect_on_analysis")

# Compile the graph
graph = graph_builder.compile()

# Function to run the code analysis agent
def run_code_analysis_agent(file_tree: str, file_contents: str, programming_language: str):
    # Initialize the agent's state
    initial_state = {
        "file_tree": file_tree,
        "file_contents": file_contents,
        "programming_language": programming_language,
        "analysis_result": "",
        "iteration": 0,
        "human_input": ""
    }
    # Invoke the state graph
    final_state = graph.invoke(initial_state)
    
    # Print intermediate and final analysis results
    for i in range(1, final_state["iteration"]):
        print(f"Reflection {i} Analysis Result:")
        print(final_state["analysis_result"])
    
    print("Final Analysis Result:")
    print(final_state["analysis_result"])
    return final_state  # Ensure the final state is returned for further processing

# # Example usage
# if __name__ == "__main__":
#     # Replace these with the actual file tree and contents from the Discovery Agent
#     file_tree = "example_file_tree"
#     file_contents = "example_file_contents"
#     programming_language = "Python"
#     run_code_analysis_agent(file_tree, file_contents, programming_language)