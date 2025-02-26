import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from typing import TypedDict
from github import Github
from langchain_core.messages import SystemMessage, HumanMessage
import pygments
from pygments.lexers import guess_lexer_for_filename, ClassNotFound
import colorama

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

# Function to gather repository content
def gather_repo_content_node(state: AgentState):
    repo_url = state["repo_url"]
    g = Github()
    try:
        # Extract the owner and repo name from the URL
        parts = repo_url.rstrip('/').split('/')
        owner, repo = parts[-2], parts[-1].replace('.git', '')

        repo = g.get_repo(f"{owner}/{repo}")
        contents = repo.get_contents("")
        file_tree = {}
        file_contents = []
        programming_languages = set()

        # Traverse the repository contents
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
                file_tree[file_content.path] = {}
            else:
                file_tree[file_content.path] = None
                try:
                    content_str = file_content.decoded_content.decode('utf-8')
                    file_contents.append(f"File: {file_content.path}\nContent:\n{content_str}\n")
                    
                    # Guess the programming language
                    try:
                        lexer = guess_lexer_for_filename(file_content.path, content_str)
                        programming_languages.add(lexer.name)
                    except ClassNotFound:
                        print(f"No lexer found for filename '{file_content.path}', skipping.")
                except UnicodeDecodeError:
                    print(f"Failed to decode file '{file_content.path}', skipping.")

        # Combine file tree and contents into strings
        file_tree_str = format_file_tree(file_tree)
        file_contents_str = "\n".join(file_contents)
        programming_languages_str = ", ".join(programming_languages)
        combined_content = f"{state['task']}\n\nHere is the file tree:\n\n{file_tree_str}\n\nHere are the file contents:\n\n{file_contents_str}\n\nProgramming Languages Used: {programming_languages_str}"

        # Create messages for the model
        messages = [
            SystemMessage(content=GATHER_REPO_CONTENT_PROMPT),
            HumanMessage(content=combined_content),
        ]

        # Invoke the model with the messages
        response = model.invoke(messages)
        return {"file_tree": file_tree_str, "file_contents": file_contents_str, "programming_languages": programming_languages_str}
    except Exception as e:
        print(f"An error occurred while fetching the repository content: {str(e)}")
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

# Function to run the agent
def run_agent(repo_url: str):
    task = "Create a file tree and gather file contents for the given GitHub repository"

    # Initialize the agent's state
    initial_state = {
        "task": task,
        "repo_url": repo_url,
        "file_tree": "",
        "file_contents": "",
        "programming_languages": "",
    }

    try:
        # Gather repository content
        final_state = gather_repo_content_node(initial_state)
        if final_state and "file_tree" in final_state and "file_contents" in final_state:
            print("Final File Tree:")
            print(colorama.Fore.YELLOW + final_state["file_tree"])
            colorama.Style.RESET_ALL
            print("Final File Contents:")
            print(final_state["file_contents"])
            print("Programming Languages Used:")
            print(colorama.Fore.GREEN + final_state["programming_languages"])
            # return final_state
            status="Success"
            return final_state
            
        

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        status=None
        return status

# Example usage
# if __name__ == "__main__":
#     repo_url = "Srirup2000/own-password-checker"
#     run_agent(repo_url)