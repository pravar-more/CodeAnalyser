# streamlit_app/app.py
import streamlit as st
# from codeAnalyser.langgraph.utils import clone_repo, analyze_repo  # Adjust the import path as needed
from pages.page1 import page1  
# Function to handle navigation
def navigate_to(page):
    st.session_state['page'] = page

# Initialize session state
if 'page' not in st.session_state:
    st.session_state['page'] = 'home'

# Navigation buttons
st.sidebar.title("Navigation")
st.sidebar.button("Go to Home", on_click=lambda: navigate_to('home'))
st.sidebar.button("Go to Page 1", on_click=lambda: navigate_to('page1'))

# Display the appropriate page based on the session state
if st.session_state['page'] == 'home':
    st.title("Home Page")
    st.write("Welcome to the Home Page!")
elif st.session_state['page'] == 'page1':
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
