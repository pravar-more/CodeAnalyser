import streamlit as st
import re
from agentic_workflow import run_agentic_workflow
from discovery_agent import run_agent
import graphviz as gv

def create_flowchart(active_node=None):
    # Create a new digraph
    flowchart = gv.Digraph()
    
    # Configure graph attributes
    flowchart.attr(rankdir='TB')  # Top to Bottom direction
    
    # Define node styles
    inactive_style = {
        'style': 'filled',
        'fillcolor': '#E5E5E5',
        'shape': 'box',
        'fontsize': '10',
        'margin': '0.2'
    }
    
    active_style = {
        'style': 'filled',
        'fillcolor': '#90EE90',  # Light green
        'shape': 'box',
        'fontsize': '10',
        'penwidth': '2',
        'margin': '0.2'
    }
    
    # Define nodes and their labels
    nodes = {
        'GitRepo': 'Git\nRepository',
        'discovery': 'Discovery\nAgent',
        'analysis': 'Code Analysis\nAgent',
        'recommendation': 'Recommendation\nAgent',
        'human': 'Human\nInput',
        'END': 'END'
    }
    
    # Add nodes with appropriate styles
    for node_id, label in nodes.items():
        style = active_style if node_id == active_node else inactive_style
        flowchart.node(node_id, label, **style)
    
    # Add edges
    flowchart.edge('GitRepo','discovery')
    flowchart.edge('discovery', 'analysis')
    flowchart.edge('analysis', 'recommendation')
    flowchart.edge('recommendation', 'human')
    flowchart.edge('human', 'analysis')
    flowchart.edge('recommendation', 'END')
    
    return flowchart
def page1(): 
    st.set_page_config(
        page_title="Git Repository Analysis",
        page_icon="🧊",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Initialize session state
    if 'response1' not in st.session_state:
        st.session_state.response1 = None
    if 'response2' not in st.session_state:
        st.session_state.response2 = None
    if 'analysis_started' not in st.session_state:
        st.session_state.analysis_started = False

    st.sidebar.header("REPO ANALYSIS")
    repo_url = st.sidebar.text_input("GIT REPO LINK")    

    is_valid_github_url = lambda url: re.match(r"^https://github.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/?$", url) is not None

    if st.sidebar.button("Analyze") or st.session_state.analysis_started:
        st.session_state.analysis_started = True
        if is_valid_github_url(repo_url):
            st.header("Analyzing..", divider=True)
            col1, col2, col3 = st.columns([0.4, 0.45, 0.15])
            container_col1 = col1.container()
            container_col3 = col3.container()
            st.sidebar.success("Valid Git Link ")
            

            # Initial flowchart with discovery node active
            container_col3.graphviz_chart(create_flowchart('discovery'))

            if st.session_state.response1 is None:
                st.session_state.response1 = run_agent(repo_url)

            if st.session_state.response1:
                st.header("Yahooo :)", divider=True)
                    
                # Define tabs and their containers
                tab1, tab2 = col2.tabs(["File Tree", "Language Used"])
                container_col2_t1 = tab1.container()
                container_col2_t2 = tab2.container()
                
                container_col1.code(st.session_state.response1["file_tree"])
                container_col2_t1.subheader("Programming Language")
                container_col2_t1.code(st.session_state.response1["programming_languages"])
                container_col2_t2.subheader("File Content")
                container_col2_t2.code(st.session_state.response1["file_contents"])
                
                # Add user input after discovery
                st.sidebar.markdown("---")
                st.sidebar.subheader("Initial Feedback")
                initial_user_input = st.sidebar.text_area(
                    "Provide your initial analysis requirements:",
                    placeholder="Example: Focus on security vulnerabilities, check code organization, etc."
                )
                
                # Update flowchart - analysis node active
                container_col3.graphviz_chart(create_flowchart('analysis'))
                  
                if st.sidebar.button("Run Code Analysis"):
                    st.session_state.response2 = run_agentic_workflow(repo_url, initial_user_input)
                
                if st.session_state.response2 and "analysis_result" in st.session_state.response2:
                    container_col1.write("Analysis complete. Check the results in the right pane.")
                    container_col2_t1.write(st.session_state.response2["analysis_result"])
                    container_col2_t2.write(st.session_state.response2["analysis_result"])
                    
                    # Update flowchart - recommendation node active
                    container_col3.graphviz_chart(create_flowchart('recommendation'))
                    
                    st.info("Kindly provide your feedback for the next iteration.")
                    st.sidebar.markdown("---")
                    st.sidebar.subheader("Human Input for Iteration 2")
                    second_user_input = st.sidebar.text_area(
                        "Enter your comments or instructions for the next iteration:",
                        placeholder="Example: Please elaborate more on the security aspects..."
                    )
                    
                    if st.sidebar.button("Submit User Input"):
                        if second_user_input:
                            # Update flowchart - human input node active
                            container_col3.graphviz_chart(create_flowchart('human'))
                            
                            st.session_state.response2 = run_agentic_workflow(repo_url, second_user_input, resume=True)
                            if st.session_state.response2 and "analysis_result" in st.session_state.response2:
                                container_col2_t2.write(st.session_state.response2["analysis_result"])
                                # Update flowchart - back to analysis for second iteration
                                container_col3.graphviz_chart(create_flowchart('analysis'))
                            else:
                                st.error("Failed to process the second iteration. Please try again.")
                                container_col3.graphviz_chart(create_flowchart('recommendation'))
                        else:
                            st.warning("Please provide feedback for the second iteration.")
                    else:
                        st.error("Failed to run code analysis. Please try again.")
                        container_col3.graphviz_chart(create_flowchart('discovery'))
            else:
                st.error("Failed to fetch repository content. Please check the repository URL and try again.")
                container_col3.graphviz_chart(create_flowchart())
        else:
            st.header("OOPSies!!!!!!", divider=True)
            st.write("No Problem")
            col1, col2 = st.columns([0.99, 0.01])
            container_col1 = col1.container()
            container_col1.subheader("Try Again!")
            st.sidebar.error("Please enter a valid Git repository URL.")
    else:
        st.header("WELCOME!", divider=True)
        col1, col2,col3 = st.columns([0.75,0.05, 0.20])
        container_col1 = col1.container()
        container_col1.write("Hello to Repo Analysis, Enter your git link in sidebar input box and click on :red[RUN] button to get the analysis.")
        # Show initial flowchart with all nodes inactive
        
        container_col3 = col3.container()
        container_col3.graphviz_chart(create_flowchart())

if __name__ == "__main__":
    page1()