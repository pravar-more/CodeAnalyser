from agentic_workflow import run_agentic_workflow
import os
from dotenv import load_dotenv
from typing import TypeDict 
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing import Annotated
from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureChatOpenAI
from github import Github
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
import pygments
from pygments.lexers import guess_lexer_for_filename, ClassNotFound

#LOAD ENVIRONMENT
load_dotenv()

#DEFINE STATE
class GraphState(TypeDict):
    messages: Annotated[list, add_messages]

#CREATE THE GRAPH 
builder = StateGraph(GraphState)

#CREATE LLM
llm = AzureChatOpenAI(
    azure_deployment=os.environ.get("AZURE_OPENAI_API_DEPLOYMENT_NAME"),
    api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
    temperature=0.1,
    max_tokens=2000,
    timeout=None,
    open_ai_key= os.environ.get("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
)














# #############################

def main():
    # Prompt the user to enter the GitHub repository URL
    repo_url = input("Enter the GitHub repository URL: ")
    
    # Run the agentic workflow
    run_agentic_workflow(repo_url)

if __name__ == "__main__":
    main()