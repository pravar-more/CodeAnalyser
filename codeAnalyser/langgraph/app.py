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

    is_valid_github_url = lambda url: re.match(r"^https://github.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/?$", url) is not None

    if st.sidebar.button("Analyze") and repo_url is not None:
        if is_valid_github_url(repo_url):
            st.header("Yahooo :)", divider=True)
            col1, col2 = st.columns([0.4, 0.6])
            container_col1 = col1.container()
            st.sidebar.success("Valid Git Link ")

            container_col1_message1 = """
                <style>
                .transparent-text {
                    color: rgba(0, 0, 0, 0.6); /* Change the opacity by adjusting the alpha value (0.5) */
                }
                </style>
                <p class="transparent-text">Analysis in progress..</p>
            """
            container_col2_message1 = """
                <style>
                .transparent-text {
                    color: rgba(0, 0, 0, 0.6); /* Change the opacity by adjusting the alpha value (0.5) */
                }
                </style>
                <p class="transparent-text">Output will be displayed here after analysis.</p>
            """

            container_col1.write(container_col1_message1, unsafe_allow_html=True)

            tab1, tab2 = col2.tabs(["Iteration 1", "Iteration 2"])
            container_col2_t1 = tab1.container()
            container_col2_t1.write(container_col2_message1, unsafe_allow_html=True)
            
            container_col2_t2 = tab2.container()
            container_col2_t2.write("Output will be displayed here after analysis.")

            response1 = run_agent(repo_url) 
            if response1:
                container_col1.code(response1["file_tree"])
                container_col2_t1.subheader("Programming Language")
                container_col2_t1.code(response1["programming_languages"])
                container_col2_t2.subheader("File Content")
                container_col2_t2.code(response1["file_contents"])
                
                input2 = st.sidebar.text_input("Enter your input here")  
                button2 = st.sidebar.button("Run Code Analysis")
                if button2:
                    response2 = run_agentic_workflow(repo_url)
                    if response2:
                        container_col1.write("Analysis complete. Check the results in the right pane.")
                        container_col2_t1.write(response2["recommendations"])
                        container_col2_t2.write(response2["recommendations"])
                        st.info("Kindly provide your feedback for the next iteration.")
                        # Collect human input for iteration 2
                        st.sidebar.subheader("Human Input for Iteration 2")
                        human_input = st.sidebar.chat_input("Enter your comments or instructions for the next iteration:")
                        # human_input = st.sidebar.text_area("Enter your comments or instructions for the next iteration:")
                        if st.sidebar.button("Submit Human Input"):
                            response2["human_input"] = human_input
                            response2 = run_agentic_workflow(repo_url)
                            container_col2_t2.write(response2["recommendations"])
                    else:
                        container_col2_t1.write("Analysis failed.")
                        container_col2_t2.write("Analysis failed.")
                else:
                    container_col1.write("Analysis failed.")
            else:
                col1, col2 = st.columns([0.99, 0.01])
                container_col1 = col1.container()
                container_col1.write("No recommendations available.")
        else:
            st.header("OOPSies!!!!!!", divider=True)
            st.write("No Problem")
            col1, col2 = st.columns([0.99, 0.01])
            container_col1 = col1.container()
            container_col1.subheader("Try Again!")
            st.sidebar.error("Please enter a valid Git repository URL.")
    else:
        st.header("WELCOME!", divider=True)
        col1, col2 = st.columns([0.99, 0.01])
        container_col1 = col1.container()
        container_col1.write("Hello to Repo Analysis, Enter your git link in sidebar input box and click on :red[RUN] button to get the analysis.")

if __name__ == "__main__":
    page1()