import os
from typing import TypedDict
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
    human_input: str  

# Define the prompt template for code analysis
PROMPT_TEMPLATE = """
You are Code Analyzer Agent (CAA), an expert AI code analyst. Your task is to analyze the provided code for potential issues based on the following instructions and guidelines.

**Human Input:**
{human_input}

**Input:**
*   **Code:**
    ```
    {code}
    ```
*   **Programming Language:** {language}
*   **Analysis Focus:** {analysis_focus} (e.g., security vulnerabilities, performance bottlenecks, code style, maintainability, specific bug patterns).
*   **Style Guide (Optional):** {style_guide} (e.g., PEP 8 for Python, Google Style Guide for Java). 
*   **Specific Instructions:** {specific_instructions}


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
    try:
        # Create the analysis prompt using the template
        specific_instructions = state['human_input'] if state['human_input'] else "Focus on code quality, security, and performance"
        
        analysis_prompt = PROMPT_TEMPLATE.format(
            code=state['file_contents'],
            language=state['programming_language'],
            analysis_focus="security vulnerabilities, performance bottlenecks, code style, maintainability",
            style_guide="PEP 8" if state['programming_language'] == "Python" else "",
            specific_instructions=specific_instructions,
            human_input=state['human_input'] if state['human_input'] else "No specific requirements provided."
        )
        # Invoke the model with the analysis prompt
        response = llm.invoke([{"role": "system", "content": analysis_prompt}])
        return {"analysis_result": response.content, "iteration": state["iteration"] + 1}
    except Exception as e:
        print(f"Error in analyze_code: {str(e)}")
        return None

# Function to reflect on the analysis
def reflect_on_analysis(state: AnalysisState):
    try:
        specific_instructions = state['human_input'] if state['human_input'] else "Focus on code quality, security, and performance"
        
        reflection_prompt = PROMPT_TEMPLATE.format(
            code=state['file_contents'],
            language=state['programming_language'],
            analysis_focus="security vulnerabilities, performance bottlenecks, code style, maintainability",
            style_guide="PEP 8" if state['programming_language'] == "Python" else "",
            specific_instructions=specific_instructions,
            human_input=state['human_input'] if state['human_input'] else "No specific requirements provided."
        )
        response = llm.invoke([{"role": "system", "content": reflection_prompt}])
        return {"analysis_result": response.content, "iteration": state["iteration"] + 1}
    except Exception as e:
        print(f"Error in reflect_on_analysis: {str(e)}")
        return None

# Function to pause for user input
def pause_for_user_input(state: AnalysisState):
    return state

# Function to determine if the analysis should continue
def should_continue(state: AnalysisState):
    if state is None:
        return END
    # Continue if the iteration count is less than 2
    if state["iteration"] >= 2:
        return END
    return "reflect_on_analysis"

# Initialize the state graph
graph_builder = StateGraph(AnalysisState)

# Add nodes
graph_builder.add_node("analyze_code", analyze_code)
graph_builder.add_node("reflect_on_analysis", reflect_on_analysis)
graph_builder.add_node("pause_for_user_input", pause_for_user_input)

# Set the entry point
graph_builder.set_entry_point("analyze_code")

# Add conditional edges
graph_builder.add_conditional_edges(
    "reflect_on_analysis",
    should_continue,
    {
        END: END,
        "reflect_on_analysis": "reflect_on_analysis",
        "pause_for_user_input": "pause_for_user_input"
    }
)

# Add edges
graph_builder.add_edge("analyze_code", "reflect_on_analysis")
graph_builder.add_edge("pause_for_user_input", "reflect_on_analysis")

# Compile the graph
graph = graph_builder.compile()

# Function to run the code analysis agent
def run_code_analysis_agent(file_tree: str, file_contents: str, programming_language: str, human_input: str = ""):
    try:
        # Initialize the agent's state
        initial_state = {
            "file_tree": file_tree,
            "file_contents": file_contents,
            "programming_language": programming_language,
            "analysis_result": "",
            "iteration": 0,
            "human_input": human_input
        }
        
        # Invoke the state graph
        final_state = graph.invoke(initial_state)
        
        if final_state is None:
            print("Analysis failed to complete")
            return None
            
        return final_state
        
    except Exception as e:
        print(f"An error occurred in the analysis: {str(e)}")
        return None

if __name__ == "__main__":
    # Example usage
    file_tree = "example_tree"
    file_contents = "example_code"
    programming_language = "Python"
    human_input = "Focus on security aspects"
    result = run_code_analysis_agent(file_tree, file_contents, programming_language, human_input)
    if result:
        print(f"Analysis Result: {result['analysis_result']}")
















