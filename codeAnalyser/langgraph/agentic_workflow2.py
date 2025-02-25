from langgraph.graph import StateGraph, END, START
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
        print("no code found, skipping this stage")
        return None
    analysis_state = run_code_analysis_agent(state["file_tree"], state["file_contents"], state["programming_languages"])
    state["analysis_result"] = analysis_state["analysis_result"]
    return state

# Function to run the Recommendation Agent
def run_recommendation(state: AgenticWorkflowState):
    if state is None:
        print("returning")
        return None

    recommendation_state = run_recommendation_agent(state["file_tree"], state["file_contents"], state["programming_languages"], state["analysis_result"])
    state["recommendations"] = recommendation_state["recommendations"]
    return state

# Initialize the state graph
graph_builder = StateGraph(AgenticWorkflowState)
graph_builder.add_node("run_discovery", run_discovery)
graph_builder.add_node("run_code_analysis", run_code_analysis)
graph_builder.add_node("run_recommendation", run_recommendation)
'''
flag = run_discovery(AgenticWorkflowState)
if flag is not None:
    graph_builder.add_node("run_code_analysis", run_code_analysis)
else:
    print("---------No code found---------")
flag = run_code_analysis(AgenticWorkflowState)
if flag is not None:
    graph_builder.add_node("run_recommendation", run_recommendation)
'''
    
# Set the entry point
graph_builder.set_entry_point("run_discovery")

# Add edges between nodes
# graph_builder.add_edge(START,"run_discovery")
#graph_builder.add_edge("run_discovery", "run_code_analysis")
#graph_builder.add_edge("run_code_analysis", "run_recommendation")

def decide_node_condition(state: AgenticWorkflowState):
    return "Success" if state.get("status") == "Success" else "None"


graph_builder.add_conditional_edges(
    "run_discovery",
    decide_node_condition,
    {
        "None": END,
        "Success": "run_code_analysis"
    }

)

graph_builder.add_conditional_edges(
    "run_code_analysis",
    decide_node_condition,
    {
        "None": END,
        "Success": "run_recommendation"
    }

)

#graph_builder.add_edge("run_recommendation", END)

# Compile the graph
graph = graph_builder.compile()

# Function to run the agentic workflow
def run_agentic_workflow(repo_url: str):
    # Initialize the agent's state
    initial_state = {
        "repo_url": repo_url,
        "file_tree": "",
        "file_contents": "",
        "programming_languages": "",
        "analysis_result": "",
        "recommendations": "",
        "iteration": 0
    }
    # Invoke the state graph
    final_state = graph.invoke(initial_state)
    
    # Print final recommendations
    if final_state:
        print("Final Recommendations:")
        print(final_state["recommendations"])
    return final_state 

if __name__ == "__main__":
    repo_url = input("Enter the GitHub repository URL: ")
    run_agentic_workflow(repo_url)