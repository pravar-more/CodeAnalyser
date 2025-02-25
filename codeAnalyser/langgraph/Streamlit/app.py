import streamlit as st
import re
from langgraph.agentic_workflow import run_agentic_workflow

def page1(): 
    st.set_page_config(
        page_title="Git Repository Analysis",
        page_icon="🧊",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    st.header("Git Repository Analysis")

    col1, col2 = st.columns([0.4, 0.6]) 

    # ###################
    # COLUMN 1
    container_col1 = col1.container()

    repo_url = col1.text_input("Enter Git Repository URL")  
    is_valid_github_url = lambda url: re.match(r'^https://github\.com/[A-Za-z0-9_-]+/[A-Za-z0-9_-]+(\.git)?$', url) is not None

    # ###################
    # COLUMN 2
    tab1, tab2 = col2.tabs(["Iteration 1", "Iteration 2"])
    
    container_col2_t1 = tab1.container()
    container_col2_t1.subheader("Iteration 1")
    container_col2_t1.write("Output will be displayed here after analysis.")
    
    container_col2_t2 = tab2.container()
    container_col2_t2.subheader("Iteration 2")
    container_col2_t2.write("Output will be displayed here after analysis.")

    if col1.button("Analyze"):
        if is_valid_github_url(repo_url):
            container_col1.success("Valid Git Link ")
            response = run_agentic_workflow(repo_url)
            if response:
                container_col1.write("Analysis complete. Check the results in the right pane.")
                container_col2_t1.write(response["recommendations"])
                container_col2_t2.write(response["recommendations"])
            else:
                container_col1.write("No recommendations available.")
        else:
            container_col1.error("Please enter a valid Git repository URL.")
    else:
        container_col1.write("Hello to Repo Analysis, Enter your link in the text input")

page1()