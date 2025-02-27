import os
import time
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from typing import TypedDict
from github import Github, GithubException
from langchain_core.messages import SystemMessage, HumanMessage
import pygments
from pygments.lexers import guess_lexer_for_filename, ClassNotFound

# Load environment variables from .env file
load_dotenv()

# Define configuration variables for the Azure OpenAI API
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
key = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_GPT4_DEPLOYMENT_NAME = os.getenv("AZURE_GPT4_DEPLOYMENT_NAME")

# Initialize an instance of AzureChatOpenAI with the specified parameters
model = AzureChatOpenAI(
    temperature=0.1,
    model=AZURE_GPT4_DEPLOYMENT_NAME,
    azure_endpoint=endpoint,
    openai_api_key=key,
    api_version=AZURE_OPENAI_API_VERSION
)

# Define a TypedDict for the agent's state
class AgentState(TypedDict):
    task: str
    repo_url: str
    file_tree: str
    file_contents: str
    programming_languages: str

# Define the prompt for gathering repository content
GATHER_REPO_CONTENT_PROMPT = """You are an expert in reading GitHub repositories. Gather the content from the given repository and create a file tree."""

def gather_repo_content_node(state: AgentState):
    repo_url = state["repo_url"]
    g = Github()
    
    try:
        # Check rate limit before making request
        rate_limit = g.get_rate_limit()
        if rate_limit.core.remaining == 0:
            reset_timestamp = rate_limit.core.reset.timestamp()
            current_timestamp = time.time()
            wait_time = int(reset_timestamp - current_timestamp)
            print(f"Rate limit exceeded. Please try again after {wait_time} seconds.")
            return None

        # Extract the owner and repo name from the URL
        parts = repo_url.rstrip('/').split('/')
        owner, repo = parts[-2], parts[-1].replace('.git', '')

        try:
            repo = g.get_repo(f"{owner}/{repo}")
        except GithubException as e:
            print(f"Repository not found or access denied: {str(e)}")
            return None

        file_tree = {}
        file_contents = []
        programming_languages = set()

        # Get initial contents
        try:
            contents = repo.get_contents("")
        except GithubException as e:
            print(f"Error accessing repository contents: {str(e)}")
            return None

        # Process repository contents with rate limit awareness
        while contents:
            try:
                file_content = contents.pop(0)
                
                # Check rate limit during processing
                if g.get_rate_limit().core.remaining == 0:
                    print("Rate limit reached while processing files. Saving partial results.")
                    break

                if file_content.type == "dir":
                    try:
                        dir_contents = repo.get_contents(file_content.path)
                        contents.extend(dir_contents)
                        file_tree[file_content.path] = {}
                    except GithubException as e:
                        print(f"Error accessing directory {file_content.path}: {str(e)}")
                        continue
                else:
                    file_tree[file_content.path] = None
                    try:
                        content_str = file_content.decoded_content.decode('utf-8')
                        file_contents.append(f"File: {file_content.path}\nContent:\n{content_str}\n")
                        
                        try:
                            lexer = guess_lexer_for_filename(file_content.path, content_str)
                            programming_languages.add(lexer.name)
                        except ClassNotFound:
                            pass
                    except UnicodeDecodeError:
                        print(f"Skipping binary file: {file_content.path}")
                        continue

            except GithubException as e:
                if "rate limit" in str(e).lower():
                    print(f"Rate limit reached while processing files. Saving partial results.")
                    break
                print(f"Error processing {file_content.path if 'file_content' in locals() else 'unknown file'}: {str(e)}")
                continue

        # Format results even if incomplete
        file_tree_str = format_file_tree(file_tree)
        file_contents_str = "\n".join(file_contents)
        programming_languages_str = ", ".join(programming_languages)

        if not file_contents_str:
            print("No readable files found in repository")
            return None

        # Create messages for the model
        combined_content = f"{state['task']}\n\nHere is the file tree:\n\n{file_tree_str}\n\nHere are the file contents:\n\n{file_contents_str}\n\nProgramming Languages Used: {programming_languages_str}"
        messages = [
            SystemMessage(content=GATHER_REPO_CONTENT_PROMPT),
            HumanMessage(content=combined_content),
        ]

        # Invoke the model with the messages
        response = model.invoke(messages)
        return {
            "file_tree": file_tree_str,
            "file_contents": file_contents_str,
            "programming_languages": programming_languages_str
        }

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return None

def format_file_tree(file_tree, indent=""):
    tree_str = ""
    for key, value in file_tree.items():
        if value is None:
            tree_str += f"{indent}├── {os.path.basename(key)}\n"
        else:
            tree_str += f"{indent}├── {os.path.basename(key)}/\n"
            tree_str += format_file_tree(value, indent + "│   ")
    return tree_str

def run_agent(repo_url: str):
    task = "Create a file tree and gather file contents for the given GitHub repository"

    initial_state = {
        "task": task,
        "repo_url": repo_url,
        "file_tree": "",
        "file_contents": "",
        "programming_languages": "",
    }

    try:
        final_state = gather_repo_content_node(initial_state)
        if final_state and "file_tree" in final_state and "file_contents" in final_state:
            return final_state
    except Exception as e:
        print(f"Error in run_agent: {str(e)}")
        return None

    return None

if __name__ == "__main__":
    repo_url = "owner/repository"
    result = run_agent(repo_url)
    if result:
        print("Successfully analyzed repository")