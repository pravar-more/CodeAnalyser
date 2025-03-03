import os
from dotenv import load_dotenv
from agentic_workflow import run_agentic_workflow
from discovery_agent import run_agent as run_discovery_agent
from code_analysis_agent import run_code_analysis_agent 
from recommendation_agent import run_recommendation_agent
import json

# Load environment variables
load_dotenv()

def analyze_project(project_path: str) -> dict:
    """
    Analyzes a project using the agentic workflow and generates a comprehensive report
    
    Args:
        project_path (str): Path to the project directory
        
    Returns:
        dict: Analysis report including code analysis, recommendations etc.
    """
    try:
        # Convert directory path to GitHub repository URL format
        repo_url = f"file://{os.path.abspath(project_path)}"
        
        # Run the agentic workflow
        final_state = run_agentic_workflow(
            repo_url=repo_url,
            user_input="Please analyze this project focusing on:\n" + 
                      "1. Code quality and maintainability\n" +
                      "2. Security vulnerabilities\n" +
                      "3. Performance optimizations\n" +
                      "4. Dependency analysis\n" +
                      "5. Best practices compliance"
        )
        
        if final_state:
            # Generate comprehensive report
            report = {
                "file_structure": final_state["file_tree"],
                "languages_used": final_state["programming_languages"],
                "code_analysis": final_state["analysis_result"],
                "recommendations": final_state["recommendations"],
                "timestamp": os.path.getmtime(project_path)
            }
            
            # Save report
            report_path = os.path.join(project_path, "analysis_report.json")
            with open(report_path, "w") as f:
                json.dump(report, f, indent=2)
                
            print(f"\nAnalysis report saved to: {report_path}")
            return report
            
        else:
            print("Failed to analyze project")
            return None
            
    except Exception as e:
        print(f"Error analyzing project: {str(e)}")
        return None

def main():
    # Get project path from environment or user input
    project_path = os.getenv("PROJECT_PATH")
    
    if not project_path:
        project_path = input("Enter the path to your project directory: ")
    
    if not os.path.exists(project_path):
        print(f"Error: Directory not found: {project_path}")
        return
        
    try:
        print(f"\nAnalyzing project at: {project_path}")
        print("\nRunning agentic workflow...")
        
        report = analyze_project(project_path)
        
        if report:
            # Print summary
            print("\n=== Analysis Complete ===")
            print("\nLanguages Detected:")
            print(report["languages_used"])
            
            print("\nKey Findings:")
            print(report["code_analysis"])
            
            print("\nRecommendations:")
            print(report["recommendations"])
            
            print(f"\nDetailed report saved to: {os.path.join(project_path, 'analysis_report.json')}")
        
    except Exception as e:
        print(f"Error in main: {str(e)}")

if __name__ == "__main__":
    main()