from agentic_workflow import run_agentic_workflow

def main():
    # Prompt the user to enter the GitHub repository URL
    repo_url = input("Enter the GitHub repository URL: ")
    print("hello world")
    # Run the agentic workflow
    run_agentic_workflow(repo_url)

if __name__ == "__main__":
    main()