from langgraph.graph import StateGraph, END
from discovery_agent import run_agent as run_discovery_agent
from code_analysis_agent import run_code_analysis_agent
from recommendation_agent import run_recommendation_agent
from typing import TypedDict

# Define the state machine for the agentic workflow
class AgenticWorkflowState(TypedDict):
    repo_url: str
    file_tree: str
    file_contents: str
    programming_languages: str
    analysis_result: str
    recommendations: str
    iteration: int
    human_input: str

# Function to run the Discovery Agent
def run_discovery(state: AgenticWorkflowState):
    try:
        discovery_result = run_discovery_agent(state["repo_url"])
        if discovery_result:
            state["file_tree"] = discovery_result["file_tree"]
            state["file_contents"] = discovery_result["file_contents"]
            state["programming_languages"] = discovery_result["programming_languages"]
            if not state["file_contents"]:
                print("No code found in the repository.")
                return None
        else:
            print(f"Repository not found: {state['repo_url']}")
            return None
    except Exception as e:
        print(f"An error occurred while fetching the repository content: {str(e)}")
        return None
    return state

# Function to run the Code Analysis Agent
def run_code_analysis(state: AgenticWorkflowState):
    if not state["file_contents"]:
        print("No code found, skipping this stage")
        return None
    analysis_state = run_code_analysis_agent(
        state["file_tree"], 
        state["file_contents"], 
        state["programming_languages"]
    )
    if analysis_state:
        state["analysis_result"] = analysis_state["analysis_result"]
    return state

# Function to run the Recommendation Agent
def run_recommendation(state: AgenticWorkflowState):
    if state is None:
        print("No state available for recommendations")
        return None
        
    recommendation_state = run_recommendation_agent(
        state["file_tree"], 
        state["file_contents"], 
        state["programming_languages"], 
        state["analysis_result"]
    )
    
    if recommendation_state:
        state["recommendations"] = recommendation_state["recommendations"]
        state["iteration"] = recommendation_state.get("iteration", 0)
    return state

# Function to determine next node
def decide_next_node(state: AgenticWorkflowState):
    if state is None:
        return END
    if state.get("iteration", 0) >= 2:
        return END
    return "run_code_analysis"

# Initialize the state graph
graph_builder = StateGraph(AgenticWorkflowState)

# Add nodes
graph_builder.add_node("run_discovery", run_discovery)
graph_builder.add_node("run_code_analysis", run_code_analysis)
graph_builder.add_node("run_recommendation", run_recommendation)

# Set the entry point
graph_builder.set_entry_point("run_discovery")

# Add edges
graph_builder.add_edge("run_discovery", "run_code_analysis")
graph_builder.add_edge("run_code_analysis", "run_recommendation")

# Add conditional edges for the feedback loop
graph_builder.add_conditional_edges(
    "run_recommendation",
    decide_next_node,
    {
        END: END,
        "run_code_analysis": "run_code_analysis"
    }
)

# Compile the graph
graph = graph_builder.compile()

def run_agentic_workflow(repo_url: str, user_input: str = "", resume: bool = False):
    """
    Run the agentic workflow with optional user input and resume functionality.
    
    Args:
        repo_url (str): The GitHub repository URL to analyze
        user_input (str): Optional user feedback for the second iteration
        resume (bool): Whether to resume from the second iteration
    """
    # Initialize the agent's state
    initial_state = {
        "repo_url": repo_url,
        "file_tree": "",
        "file_contents": "",
        "programming_languages": "",
        "analysis_result": "",
        "recommendations": "",
        "iteration": 0,
        "human_input": user_input
    }
    
    try:
        if resume:
            # Resume workflow with user input for second iteration
            initial_state["iteration"] = 1
            final_state = graph.invoke(initial_state)
        else:
            # Start workflow from beginning
            final_state = graph.invoke(initial_state)
        
        return final_state
        
    except Exception as e:
        print(f"An error occurred in the workflow: {str(e)}")
        return None

if __name__ == "__main__":
    repo_url = input("Enter the GitHub repository URL: ")
    run_agentic_workflow(repo_url)