from langgraph.graph import StateGraph, END
from discovery_agent import run_agent as run_discovery_agent
from code_analysis_agent import run_code_analysis_agent
from recommendation_agent import run_recommendation_agent
from typing import TypedDict

class AgenticWorkflowState(TypedDict):
    repo_url: str
    file_tree: str
    file_contents: str
    programming_languages: str
    analysis_result: str
    recommendations: str
    iteration: int
    human_input: str

def run_discovery(state: AgenticWorkflowState):
    """Discovers repository content and structure"""
    try:
        discovery_result = run_discovery_agent(state["repo_url"])
        if discovery_result:
            state["file_tree"] = discovery_result["file_tree"]
            state["file_contents"] = discovery_result["file_contents"]
            state["programming_languages"] = discovery_result["programming_languages"]
            if not state["file_contents"]:
                print("No code found in the repository.")
                return None
            return state
        else:
            print(f"Repository not found: {state['repo_url']}")
            return None
    except Exception as e:
        print(f"Discovery error: {str(e)}")
        return None

def run_code_analysis(state: AgenticWorkflowState):
    """Analyzes code with focus on Java-specific patterns"""
    if not state["file_contents"]:
        print("No code found, skipping analysis stage")
        return None
    
    try:
        analysis_state = run_code_analysis_agent(
            state["file_tree"],
            state["file_contents"],
            state["programming_languages"],
            state.get("human_input", "")  # Pass human input for focused analysis
        )
        
        if analysis_state:
            state["analysis_result"] = analysis_state["analysis_result"]
            return state
        return None
    except Exception as e:
        print(f"Analysis error: {str(e)}")
        return None

def run_recommendation(state: AgenticWorkflowState):
    """Generates recommendations based on analysis"""
    if state is None:
        print("No state available for recommendations")
        return None
    
    try:
        recommendation_state = run_recommendation_agent(
            state["file_tree"],
            state["file_contents"],
            state["programming_languages"],
            state["analysis_result"],
            state.get("human_input", "")
        )
        
        if recommendation_state:
            state["recommendations"] = recommendation_state["recommendations"]
            state["iteration"] = recommendation_state.get("iteration", 0)
            return state
        return None
    except Exception as e:
        print(f"Recommendation error: {str(e)}")
        return None

def decide_next_node(state: AgenticWorkflowState):
    """Determines workflow progression"""
    if state is None:
        return END
    if state.get("iteration", 0) >= 2:  # Max 2 iterations
        return END
    return "run_code_analysis"  # Continue with analysis

# Initialize workflow graph
graph_builder = StateGraph(AgenticWorkflowState)

# Add nodes
graph_builder.add_node("run_discovery", run_discovery)
graph_builder.add_node("run_code_analysis", run_code_analysis)
graph_builder.add_node("run_recommendation", run_recommendation)

# Set entry point
graph_builder.set_entry_point("run_discovery")

# Add edges
graph_builder.add_edge("run_discovery", "run_code_analysis")
graph_builder.add_edge("run_code_analysis", "run_recommendation")

# Add conditional edges for feedback loop
graph_builder.add_conditional_edges(
    "run_recommendation",
    decide_next_node,
    {
        END: END,
        "run_code_analysis": "run_code_analysis"
    }
)

# Compile graph
graph = graph_builder.compile()

def run_agentic_workflow(repo_url: str, user_input: str = "", resume: bool = False):
    """
    Runs the complete analysis workflow
    
    Args:
        repo_url (str): GitHub repository URL
        user_input (str): Optional user feedback
        resume (bool): Whether to resume from previous analysis
    """
    try:
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
        
        if resume:
            # Resume workflow with user input for second iteration
            initial_state["iteration"] = 1
            final_state = graph.invoke(initial_state)
        else:
            # Start workflow from beginning
            final_state = graph.invoke(initial_state)
            
        return final_state
        
    except Exception as e:
        print(f"Workflow error: {str(e)}")
        return None

if __name__ == "__main__":
    # Test workflow
    repo_url = input("Enter the GitHub repository URL: ")
    result = run_agentic_workflow(repo_url)
    if result:
        print("\nAnalysis Complete!")
        print(f"Languages: {result['programming_languages']}")
        print("\nRecommendations:")
        print(result["recommendations"])