# streamlit_app/app.py
import streamlit as st
# from codeAnalyser.langgraph.utils import clone_repo, analyze_repo  # Adjust the import path as needed
import sys
import re
from langgraph.agentic_workflow import run_agentic_workflow


def page1():  
    st.title("Git Repository Analysis")
    repo_url = st.text_input("Enter Git Repository URL")


    #
    is_valid_github_url = lambda url: re.match(r'^https://github\.com/[A-Za-z0-9_-]+/[A-Za-z0-9_-]+(\.git)?$', url) is not None
    if st.button("Analyze"):
        if is_valid_github_url(repo_url):
            st.success("Valid Git Link ")
            st.write("Cloning and analyzing the repository...")
        else:
            st.error("Please enter a valid Git repository URL.")    

    else:
        st.write("Bye Bye")


page1()







# if st.button("Analyze"):
#     if repo_url:
#         st.write("Cloning and analyzing the repository...")
#         clone_dir = clone_repo(repo_url)
#         file_counts_df, languages_df = analyze_repo(clone_dir)
        
#         st.subheader("Folder Structure Analysis")
#         st.dataframe(file_counts_df)
        
#         st.subheader("Languages and Tools Used")
#         st.dataframe(languages_df)
#     else:
#         st.error("Please enter a valid Git repository URL.")
