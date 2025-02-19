# streamlit_app/app.py
import streamlit as st
from langgraph.utils import clone_repo, analyze_repo  # Adjust the import path as needed

st.title("Git Repository Analysis")
repo_url = st.text_input("Enter Git Repository URL")

if st.button("Analyze"):
    if repo_url:
        st.write("Cloning and analyzing the repository...")
        clone_dir = clone_repo(repo_url)
        file_counts_df, languages_df = analyze_repo(clone_dir)
        
        st.subheader("Folder Structure Analysis")
        st.dataframe(file_counts_df)
        
        st.subheader("Languages and Tools Used")
        st.dataframe(languages_df)
    else:
        st.error("Please enter a valid Git repository URL.")
