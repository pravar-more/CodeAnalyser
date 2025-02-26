import streamlit as st
import re
from agentic_workflow import run_agentic_workflow
from discovery_agent import run_agent

def page1(): 
    st.set_page_config(
        page_title="Git Repository Analysis",
        page_icon="🧊",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.sidebar.header("REPO ANALYSIS")
    repo_url = st.sidebar.text_input("GIT REPO LINK")    

    # col1, col2 = st.columns([0.4, 0.6]) 

    # ###################
    # COLUMN 1
    # container_col1 = col1.container(height=200,border=True)

    # repo_url = col1.text_input("Enter Git Repository URL")  
    is_valid_github_url = lambda url: re.match(r"^https://github.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/?$", url) is not None

    # ###################
    # COLUMN 2
    # tab1, tab2 = col2.tabs(["Iteration 1", "Iteration 2"])
    
    # container_col2_t1 = tab1.container(height=300)
    # container_col2_t1.subheader("Iteration 1")
    # container_col2_t1.write("Output will be displayed here after analysis.")
    
    # container_col2_t2 = tab2.container(height=300)
    # container_col2_t2.subheader("Iteration 2")
    # container_col2_t2.write("Output will be displayed here after analysis.")

    if st.sidebar.button(":green-background[GO]", use_container_width=False):
        if is_valid_github_url(repo_url):
            st.header("Yahooo :)",divider=True)
            col1, col2 = st.columns([0.4, 0.6])
            container_col1 = col1.container(height=360,border=True)
            st.sidebar.success("Valid Git Link ")

            container_col1_message1 = """
                <style>
                .transparent-text {
                    color: rgba(0, 0, 0, 0.6); /* Change the opacity by adjusting the alpha value (0.5) */
                }
                </style>
                <p class="transparent-text">Analysis in progress..</p>
                
            """
            container_col2_message1= """
                <style>
                .transparent-text {
                    color: rgba(0, 0, 0, 0.6); /* Change the opacity by adjusting the alpha value (0.5) */
                }
                </style>
                <p class="transparent-text">Output will be displayed here after analysis.</p>
                
            """

            container_col1.write(container_col1_message1, unsafe_allow_html=True)

            tab1, tab2 = col2.tabs(["Iteration 1", "Iteration 2"])
            container_col2_t1 = tab1.container(height=300)
            container_col2_t1.subheader("Iteration 1")
            container_col2_t1.write(container_col2_message1,unsafe_allow_html=True)
            
            container_col2_t2 = tab2.container(height=300)
            container_col2_t2.subheader("Iteration 2")
            container_col2_t2.write("Output will be displayed here after analysis.")

            response1 = run_agent(repo_url) 
            if response1:
                container_col1.code(response1["file_tree"])
                
                # if container_col1.button("Click to view file contents"):
                if col1.button("Click to view file contents"):
                    container_col2_t1.write(response1["programming_languages"])
                    container_col2_t2.write(response1["file_contents"])

                #

                input2 = col1.text_input("Enter your input here")  
                
                if col1.button("Run Code Analysis"):
                    response2 = False   
                    response2= run_agentic_workflow(repo_url)
                    if response2:
                        container_col1.write("Analysis complete. Check the results in the right pane.")
                        container_col2_t1.write(response2["recommendations"])
                        container_col2_t2.write(response2["recommendations"])
                    else:
                        container_col2_t1.write("Analysis failed.")
                        container_col2_t2.write("Analysis failed.")
                else:
                    container_col1.write("Analysis failed.")
               
            else:
                col1, col2 = st.columns([0.99, 0.01])
                container_col1 = col1.container(height=360,border=True)
                container_col1.write("No recommendations available.")
        else:
            st.header("OOPSies!!!!!!",divider=True)
            st.write("No Problem")
            col1, col2 = st.columns([0.99, 0.01])
            container_col1 = col1.container(height=200,border=True)
            container_col1.subheader("Try Again!")
            st.sidebar.error("Please enter a valid Git repository URL.")
    else:
        st.header("WELCOME!",divider=True)
        col1, col2 = st.columns([0.99, 0.01])
        container_col1 = col1.container(height=200,border=True)
        container_col1.write("Hello to Repo Analysis, Enter your git link in sidebar input box and click on :red[RUN] button to get the analysis.")




if __name__ == "__main__":
    page1()