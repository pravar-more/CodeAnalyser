import streamlit as st
from agentic_workflow import run_agentic_workflow
import graphviz as gv
import re

def create_flowchart(active_node=None):
    # Create a new digraph
    flowchart = gv.Digraph()
    flowchart.attr(rankdir='TB')
    
    # Define node styles
    inactive_style = {
        'style': 'filled',
        'fillcolor': '#E5E5E5',
        'shape': 'box',
        'fontsize': '10',
        'fontname': 'Arial Bold',
        'margin': '0.05'
    }
    
    active_style = {
        'style': 'filled',
        'fillcolor': '#90EE90',
        'shape': 'box',
        'fontsize': '10',
        'penwidth': '2',
        'fontname': 'Arial Bold',
        'margin': '0.05'
    }
    
    # Define nodes and their labels
    nodes = {
        'Repo': 'Repo Connect',
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
    flowchart.edge('Repo', 'discovery')
    flowchart.edge('discovery', 'analysis')
    flowchart.edge('analysis', 'recommendation')
    flowchart.edge('recommendation', 'human')
    flowchart.edge('human', 'analysis')
    flowchart.edge('recommendation', 'END')
    
    return flowchart

# Initialize Streamlit page
st.set_page_config(
    page_title="TechStack_Governance",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        
    }
)
# Initialize session states
if 'workflow_stage' not in st.session_state:
    st.session_state.workflow_stage = None
if 'active_node' not in st.session_state:
    st.session_state.active_node = None
if 'flowchart_container' not in st.session_state:
    st.session_state.flowchart_container = None
if 'col2_container' not in st.session_state:
    st.session_state.col2_container = None
if 'human_input' not in st.session_state:
    st.session_state.human_input = ""
if 'repo_url' not in st.session_state:
    st.session_state.repo_url = ""

# Create layout
col1, col2, col3 = st.columns([0.01, 0.84, 0.15])

# Sidebar
# Sidebar
with st.sidebar:
    st.title("Agenti Workflow")
    repo_url = st.text_input("Enter the GitHub repository URL:", value=st.session_state.repo_url)
    st.session_state.repo_url = repo_url
    run_workflow_button = st.button("Run Workflow")
    
    # Add user input section after run workflow button
    st.markdown("---")
    st.subheader("Analysis Agent Input")
    st.session_state.human_input = st.text_area(
        "Specify analysis focus:",
        value=st.session_state.human_input,
        placeholder="Example: Focus on security aspects, code organization, performance...",
        key="human_input_area"
    )
    submit_input_button = st.button("Processes Feedback ")
    
# Main content area
# if not st.session_state.workflow_stage or st.session_state.active_node == 'discovery':
#     st.header("")

# Initialize containers
with col2:
    if not st.session_state.col2_container:
        st.session_state.col2_container = st.empty()
    
    # Show welcome message initially
    if not st.session_state.workflow_stage:
        with st.session_state.col2_container.container():
            st.success("WELCOME TO THE AGENTIC WORKFLOW")
            st.markdown("This tool will guide you through the process of analyzing a GitHub repository.")
            st.markdown("Please enter the URL of the repository you want to analyze and click 'Run Workflow'.")

# Flowchart area
with col3:
    if not st.session_state.flowchart_container:
        st.session_state.flowchart_container = st.empty()
    st.session_state.flowchart_container.graphviz_chart(
        create_flowchart(st.session_state.active_node)
    )

# Handle workflow button
if run_workflow_button:
    if not repo_url:
        st.error("Please enter a GitHub repository URL.")
    else:
        try:
            with st.spinner('Analyzing repository...'):
                # Update to discovery phase
                
                st.session_state.active_node = 'discovery'
                st.session_state.flowchart_container.graphviz_chart(
                    create_flowchart(st.session_state.active_node)
                )
                user_input = ""
                final_state = run_agentic_workflow(repo_url,user_input,resume=True)
                
                if final_state:
                    # Update to analysis phase
                    st.session_state.active_node = 'analysis'
                    st.session_state.flowchart_container.graphviz_chart(
                        create_flowchart(st.session_state.active_node)
                    )
                    
                    # Display results
                    with st.session_state.col2_container.container():
                        st.subheader("File Tree:")
                        st.code(final_state["file_tree"])
                        st.subheader("Programming Languages Used:")
                        st.write(final_state["programming_languages"])
                        st.markdown("---")
                        st.subheader("Analysis Report:")
                        st.write(final_state["analysis_result"])
                    
                    # Move to reflection phase
                    st.session_state.workflow_stage = 'reflection'
                    st.session_state.active_node = 'analysis'
                    st.session_state.flowchart_container.graphviz_chart(
                        create_flowchart(st.session_state.active_node)
                    )
                    st.info("Please provide your feedback in the sidebar for the next iteration.")
                else:
                    st.error("Failed to analyze repository. Please check the URL and try again.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Handle feedback submission
if submit_input_button:
    if not st.session_state.human_input:
        st.session_state.active_node = 'recommendation'
        st.warning("Please provide feedback before submitting.")
    else:
        try:
            with st.spinner('Processing feedback...'):
                # Update to human input phase
                st.session_state.active_node = 'human'
                st.session_state.flowchart_container.graphviz_chart(
                    create_flowchart(st.session_state.active_node)
                )
                
                final_state = run_agentic_workflow(
                    st.session_state.repo_url,
                    st.session_state.human_input,
                    resume=True
                )
                st.session_state.active_node = 'recommendation'
                
                if final_state:
                    # Update to final analysis phase
                    st.session_state.active_node = 'END'
                    
                    # Display updated results
                    with st.session_state.col2_container.container():
                        st.subheader("Updated Analysis Based on Feedback:")
                        st.write(final_state["analysis_result"])
                        st.markdown("---")
                        st.subheader("Final Recommendations:")
                        st.write(final_state["recommendations"])
                    
                    # Update flowchart
                    st.session_state.flowchart_container.graphviz_chart(
                        create_flowchart(st.session_state.active_node)
                    )
                else:
                    st.error("Failed to process feedback. Please try again.")
        except Exception as e:
            st.error(f"An error occurred while processing feedback: {str(e)}")