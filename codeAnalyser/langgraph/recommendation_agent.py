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

# --- Human Input Function ---
def get_human_input(state: RecommendationState) -> RecommendationState:
    """Collects human input for the recommendation agent."""
    print("\nPlease review the repository details and provide any additional comments or instructions.")
    human_input = input("Enter your comments or instructions: ")
    state["human_input"] = human_input
    return state

# Define the prompt template for generating recommendations
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

# Function to generate recommendations
def generate_recommendations(state: RecommendationState):
    # Create the recommendation prompt using the template
    recommendation_prompt = PROMPT_TEMPLATE.format(
        file_tree=state['file_tree'],
        file_contents=state['file_contents'],
        programming_languages=state['programming_languages'],
        analysis_result=state['analysis_result'],
        human_input=state['human_input']
    )
    # Invoke the model with the recommendation prompt
    response = llm.invoke([{"role": "system", "content": recommendation_prompt}])
    return {"recommendations": response.content, "iteration": state["iteration"] + 1}

# Function to reflect on the recommendations
def reflect_on_recommendations(state: RecommendationState):
    # Create the reflection prompt using the template
    reflection_prompt = PROMPT_TEMPLATE.format(
        file_tree=state['file_tree'],
        file_contents=state['file_contents'],
        programming_languages=state['programming_languages'],
        analysis_result=state['analysis_result'],
        human_input=state['human_input']
    )
    # Invoke the model with the reflection prompt
    response = llm.invoke([{"role": "system", "content": reflection_prompt}])
    return {"recommendations": response.content, "iteration": state["iteration"] + 1}

# Function to determine if the reflection should continue
def should_continue(state: RecommendationState):
    # Continue if the iteration count is less than 2
    if state["iteration"] >= 2:
        return END
    return "reflect_on_recommendations"

# Initialize the state graph
graph_builder = StateGraph(RecommendationState)
graph_builder.add_node("get_human_input", get_human_input)
graph_builder.add_node("generate_recommendations", generate_recommendations)
graph_builder.add_node("reflect_on_recommendations", reflect_on_recommendations)

# Set the entry point
graph_builder.set_entry_point("get_human_input")

# Add conditional edges
graph_builder.add_conditional_edges(
    "reflect_on_recommendations",
    should_continue,
    {END: END, "reflect_on_recommendations": "reflect_on_recommendations"},
)

# Add edge from get_human_input to generate_recommendations
graph_builder.add_edge("get_human_input", "generate_recommendations")
# Add edge from generate_recommendations to reflect_on_recommendations
graph_builder.add_edge("generate_recommendations", "reflect_on_recommendations")

# Compile the graph
graph = graph_builder.compile()

# Function to run the recommendation agent
def run_recommendation_agent(file_tree: str, file_contents: str, programming_languages: str, analysis_result: str):
    # Initialize the agent's state
    initial_state = {
        "file_tree": file_tree,
        "file_contents": file_contents,
        "programming_languages": programming_languages,
        "analysis_result": analysis_result,
        "recommendations": "",
        "iteration": 0,
        "human_input": ""
    }
    # Invoke the state graph
    final_state = graph.invoke(initial_state)
    
    # Print intermediate and final recommendation results
    for i in range(1, final_state["iteration"]):
        print(f"Reflection {i} Recommendation Result:")
        print(final_state["recommendations"])
    
    print("Final Recommendation Result:")
    print(final_state["recommendations"])
    return final_state  # Ensure the final state is returned for further processing