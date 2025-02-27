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

# Define a TypedDict for the recommendation state
class RecommendationState(TypedDict):
    file_tree: str
    file_contents: str
    programming_languages: str
    analysis_result: str
    recommendations: str
    iteration: int
    human_input: str

# Define the prompt template
PROMPT_TEMPLATE = """
You are Recommendations Agent (RA), an expert AI code analyst. Your task is to analyze the provided code and file structure for potential issues based on the following instructions and guidelines.

**Human_input:**
{human_input}

**Input:**
* **File Tree Structure:**
    ```
    {file_tree}
    ```
* **Code Content:**
    ```
    {file_contents}
    ```
* **Programming Languages:** {programming_languages}
* **Code Analysis Report:**
    ```
    {analysis_result}
    ```

**Guardrails:**
* **Security:**
    * DO NOT expose any PII, secrets, API keys, passwords, or confidential data. Redact them immediately.
    * DO NOT execute the provided code.
    * Avoid suggesting dangerous operations that could introduce security vulnerabilities.
* **Factuality & Accuracy:**
    * All reported issues MUST be backed by evidence from the code (cite line numbers).
    * Avoid speculation. If you are unsure, state your uncertainty.
    * Stay within the specified scope.
* **Ethics & Bias:**
    * Use neutral and objective language.
    * Avoid biases related to coding style, language preference, or coding patterns.

**Output Format:**
* Use a structured Markdown format for the analysis.
* Be concise and actionable.
* Prioritize high-severity issues.

**Output Format (Markdown):**
```markdown
## Recommendations Report

### Summary

[Brief overview of the recommendations. Mention key areas for improvement.]

### High Priority Recommendations

[List recommendations that address significant risks, such as security vulnerabilities or critical errors. For each recommendation:]

* **Issue:** [Brief description of the issue]
* **Recommendation:** [Detailed steps to address the issue]
* **Rationale:** [Explanation of why this recommendation is important]

### Medium Priority Recommendations

[List recommendations that address potential errors, performance problems, or maintainability issues. Follow the same format as above.]

* **Issue:** ...
* **Recommendation:** ...
* **Rationale:** ...

### Low Priority Recommendations

[List minor recommendations, such as style improvements or minor optimizations. Follow the same format as above.]

* **Issue:** ...
* **Recommendation:** ...
* **Rationale:** ...

### Conclusion

[Concluding remarks summarizing the overall recommendations and highlighting key areas for improvement.]
"""


def generate_recommendations(state: RecommendationState):
    try:
        # Create the recommendation prompt using the template
        recommendation_prompt = PROMPT_TEMPLATE.format(
            file_tree=state['file_tree'],
            file_contents=state['file_contents'],
            programming_languages=state['programming_languages'],
            analysis_result=state['analysis_result'],
            human_input=state['human_input'] if state['human_input'] else "No specific requirements provided."
        )
        # Invoke the model with the recommendation prompt
        response = llm.invoke([{"role": "system", "content": recommendation_prompt}])
        return {"recommendations": response.content, "iteration": state["iteration"] + 1}
    except Exception as e:
        print(f"Error in generate_recommendations: {str(e)}")
        return None

def reflect_on_recommendations(state: RecommendationState):
    try:
        # Create the reflection prompt using the template
        reflection_prompt = PROMPT_TEMPLATE.format(
            file_tree=state['file_tree'],
            file_contents=state['file_contents'],
            programming_languages=state['programming_languages'],
            analysis_result=state['analysis_result'],
            human_input=state['human_input'] if state['human_input'] else "No specific requirements provided."
        )
        # Invoke the model with the reflection prompt
        response = llm.invoke([{"role": "system", "content": reflection_prompt}])
        return {"recommendations": response.content, "iteration": state["iteration"] + 1}
    except Exception as e:
        print(f"Error in reflect_on_recommendations: {str(e)}")
        return None

def should_continue(state: RecommendationState):
    if state is None:
        return END
    if state.get("iteration", 0) >= 2:
        return END
    return "reflect_on_recommendations"

# Initialize the state graph
graph_builder = StateGraph(RecommendationState)

# Add nodes
graph_builder.add_node("generate_recommendations", generate_recommendations)
graph_builder.add_node("reflect_on_recommendations", reflect_on_recommendations)

# Set the entry point
graph_builder.set_entry_point("generate_recommendations")

# Add conditional edges
graph_builder.add_conditional_edges(
    "reflect_on_recommendations",
    should_continue,
    {END: END, "reflect_on_recommendations": "reflect_on_recommendations"},
)

# Add edge from generate_recommendations to reflect_on_recommendations
graph_builder.add_edge("generate_recommendations", "reflect_on_recommendations")

# Compile the graph
graph = graph_builder.compile()

def run_recommendation_agent(file_tree: str, file_contents: str, programming_languages: str, analysis_result: str, human_input: str = ""):
    """
    Run the recommendation agent with the given inputs and optional human feedback.
    
    Args:
        file_tree (str): The repository file structure
        file_contents (str): The contents of the files
        programming_languages (str): The programming languages used
        analysis_result (str): The analysis results from the code analysis agent
        human_input (str, optional): Human feedback for recommendations
    """
    try:
        # Validate inputs
        if not file_contents or not analysis_result:
            print("Missing required inputs for recommendations")
            return None
            
        # Initialize the agent's state
        initial_state = {
            "file_tree": file_tree,
            "file_contents": file_contents,
            "programming_languages": programming_languages,
            "analysis_result": analysis_result,
            "recommendations": "",
            "iteration": 0,
            "human_input": human_input
        }
        
        # Invoke the state graph
        final_state = graph.invoke(initial_state)
        
        if final_state is None:
            print("Failed to generate recommendations")
            return None
            
        return final_state
        
    except Exception as e:
        print(f"An error occurred in run_recommendation_agent: {str(e)}")
        return None

if __name__ == "__main__":
    # Example usage
    file_tree = "example_tree"
    file_contents = "example_code"
    programming_languages = "Python"
    analysis_result = "example_analysis"
    human_input = "Focus on security aspects"
    result = run_recommendation_agent(
        file_tree, 
        file_contents, 
        programming_languages, 
        analysis_result, 
        human_input
    )
    if result:
        print(f"Recommendations: {result['recommendations']}")



