from agentic_workflow import run_agentic_workflow, run_discovery

def main():
    # Prompt the user to enter the GitHub repository URL
    repo_url = input("Enter the GitHub repository URL: ")
    print("hello world")
    # Run the agentic workflow
    # run_agentic_workflow(repo_url)

    initial_state = {
        "repo_url": repo_url,
        "file_tree": "",
        "file_contents": "",
        "programming_languages": "",
        "analysis_result": "",
        "recommendations": "",
        "iteration": 0
    }
    final_state = run_discovery(initial_state)
    print("----------------------------------------------------------")
    print("----------------------------------------------------------")
    print("----------------------------------------------------------")
    print(str(final_state["file_tree"]))

if __name__ == "__main__":
    main()