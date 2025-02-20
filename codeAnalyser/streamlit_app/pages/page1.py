# streamlit_app/pages/page1.py
import streamlit as st
import re
# from streamlit_app.components.component1 import show_repo_info


def page1():  
    st.title("Git Repository Analysis")
    repo_url = st.text_input("Enter Git Repository URL")


    #
    is_valid_github_url = lambda url: re.match(r'^https://github\.com/[A-Za-z0-9_-]+/[A-Za-z0-9_-]+(\.git)?$', url) is not None
    if st.button("Analyze"):
        if is_valid_github_url(repo_url):
            st.success("Valid Git Link ")
        else:
            st.error("Please enter a valid Git repository URL.")    

    else:
        st.write("Bye Bye")


page1()







# def page1():
#     st.title("Page 1 - Repository Information")
#     repo_url = st.text_input("Enter Git Repository URL for Page 1")
#     if repo_url:
#         show_repo_info(repo_url)
#     else:
#         st.write("hello not available")
