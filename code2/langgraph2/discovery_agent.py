import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from typing import TypedDict
from github import Github, GithubException
from langchain_core.messages import SystemMessage, HumanMessage
import pygments
from pygments.lexers import guess_lexer_for_filename, ClassNotFound
import time

# Load environment variables
load_dotenv()

# Initialize Azure OpenAI
llm = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_GPT4_DEPLOYMENT_NAME"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    temperature=0.1
)

class AgentState(TypedDict):
    task: str
    repo_url: str
    file_tree: str
    file_contents: str
    programming_languages: str

DISCOVERY_PROMPT = """
You are the Discovery Agent, an expert in analyzing GitHub repositories.
Your task is to:
1. Create a file tree structure
2. Gather relevant file contents
3. Identify programming languages used
4. Focus on Java-specific files and configurations

For Java projects, pay special attention to:
-