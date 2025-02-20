# streamlit_app/pages/page1.py
import streamlit as st
# from streamlit_app.components.component1 import show_repo_info


def page1():  
    st.title("Git Repository Analysis")
    repo_url = st.text_input("Enter Git Repository URL")
    if st.button("Analyze"):
        if repo_url:
            st.write("hello world")
        else:
            st.write("Please enter a valid Git repository URL.")    

    else:
        st.write("hello not available")










# def page1():
#     st.title("Page 1 - Repository Information")
#     repo_url = st.text_input("Enter Git Repository URL for Page 1")
#     if repo_url:
#         show_repo_info(repo_url)
#     else:
#         st.write("hello not available")
