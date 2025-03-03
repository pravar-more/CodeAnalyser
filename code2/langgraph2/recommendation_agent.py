import os
from typing import TypedDict
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langgraph.graph import StateGraph, END

# Load environment variables
load_dotenv()

# Initialize Azure OpenAI
llm = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_GPT4_DEPLOYMENT_NAME"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    temperature=0.1
)

class RecommendationState(TypedDict):
    file_tree: str
    file_contents: str
    programming_languages: str
    analysis_result: str
    recommendations: str
    iteration: int
    human_input: str

JAVA_ANALYSIS_PROMPT = """
You are a Java Code Analysis Expert. Analyze the provided Java project and generate recommendations based on:

1. Code Quality:
   - Variable naming clarity and Java conventions
   - Documentation completeness (Javadoc)
   - Code organization and modularity
   - Hardcoded credentials detection

2. Security Issues:
   - Injection vulnerabilities
   - Authentication mechanisms
   - Hardcoded secrets
   - Secure communication patterns

3. Dependency Analysis:
   - Maven/Gradle dependencies
   - Version status (outdated/current)
   - License compliance
   - Known vulnerabilities

4. Performance:
   - Logic efficiency
   - Resource management
   - Database operations
   - Caching implementation

5. Best Practices:
   - Exception handling
   - Logging implementation
   - Unit test coverage
   - Design patterns usage

**Input:**
File Tree:
{file_tree}

Code Contents:
{file_contents}

Languages: {programming_languages}

Analysis Results:
{analysis_result}

Human Input:
{human_input}

Generate a detailed report in the following format:

## Java Project Analysis Report

### Project Overview
[Brief overview of project structure and components]

### Critical Issues
- Issue: [Description]
  Location: [File path and line numbers]
  Impact: [Security/Performance/Maintainability]
  Recommendation: [Specific steps to address]

### Dependency Review
| Dependency | Current Version | Latest Version | Status | Security Issues |
|------------|----------------|----------------|--------|-----------------|
[List dependencies]

### Code Quality Assessment
- Naming Conventions: [Analysis]
- Documentation: [Coverage analysis]
- Code Organization: [Structure review]

### Security Analysis
- Authentication Review: [Analysis]
- Credential Management: [Review]
- Injection Prevention: [Analysis]

### Performance Optimization
- Resource Management: [Analysis]
- Query Optimization: [Review]
- Caching Strategy: [Recommendations]

### Action Items
1. [High priority tasks]
2. [Medium priority tasks]
3. [Low priority tasks]
"""

def generate_recommendations(state: RecommendationState):
    try:
        recommendation_prompt = JAVA_ANALYSIS_PROMPT.format(
            file_tree=state['file_tree'],
            file_contents=state['file_contents'],
            programming_languages=state['programming_languages'],
            analysis_result=state['analysis_result'],
            human_input=state.get('human_input', 'No specific requirements provided.')
        )
        
        response = llm.invoke([{"role": "system", "content": recommendation_prompt}])
        return {
            "recommendations": response.content,
            "iteration": state["iteration"] + 1
        }
    except Exception as e:
        print(f"Error generating recommendations: {str(e)}")
        return None

def reflect_on_recommendations(state: RecommendationState):
    try:
        # Add Java-specific reflection prompts
        reflection_prompt = JAVA_ANALYSIS_PROMPT.format(
            file_tree=state['file_tree'],
            file_contents=state['file_contents'],
            programming_languages=state['programming_languages'],
            analysis_result=state['analysis_result'],
            human_input=f"Review previous recommendations and refine: {state['recommendations']}"
        )
        
        response = llm.invoke([{"role": "system", "content": reflection_prompt}])
        return {
            "recommendations": response.content,
            "iteration": state["iteration"] + 1
        }
    except Exception as e:
        print(f"Error in reflection: {str(e)}")
        return None

def should_continue(state: RecommendationState):
    if state is None:
        return END
    if state["iteration"] >= 2:
        return END
    return "reflect_on_recommendations"

# Initialize state graph
graph_builder = StateGraph(RecommendationState)
graph_builder.add_node("generate_recommendations", generate_recommendations)
graph_builder.add_node("reflect_on_recommendations", reflect_on_recommendations)

# Set entry point
graph_builder.set_entry_point("generate_recommendations")

# Add edges
graph_builder.add_conditional_edges(
    "reflect_on_recommendations",
    should_continue,
    {END: END, "reflect_on_recommendations": "reflect_on_recommendations"}
)
graph_builder.add_edge("generate_recommendations", "reflect_on_recommendations")

# Compile graph
graph = graph_builder.compile()

def run_recommendation_agent(file_tree: str, file_contents: str, programming_languages: str, analysis_result: str, human_input: str = ""):
    try:
        initial_state = {
            "file_tree": file_tree,
            "file_contents": file_contents,
            "programming_languages": programming_languages,
            "analysis_result": analysis_result,
            "recommendations": "",
            "iteration": 0,
            "human_input": human_input
        }
        
        final_state = graph.invoke(initial_state)
        return final_state
    except Exception as e:
        print(f"Error running recommendation agent: {str(e)}")
        return None

if __name__ == "__main__":
    # Test the agent
    test_state = {
        "file_tree": "example/tree",
        "file_contents": "public class Test {}",
        "programming_languages": "Java",
        "analysis_result": "Initial analysis",
        "human_input": "Focus on security"
    }
    result = run_recommendation_agent(**test_state)
    if result:
        print(f"Recommendations: {result['recommendations']}")