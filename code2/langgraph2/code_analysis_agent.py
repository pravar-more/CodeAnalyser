from typing import TypedDict
from langchain_openai import AzureChatOpenAI
import os

class CodeAnalysisState(TypedDict):
    code_content: str
    analysis_result: dict
    language: str
    
ANALYSIS_PROMPT = """
Analyze the provided Java code with focus on:

1. Code Quality Analysis:
   - Variable naming and clarity
   - Code modularity and organization 
   - Documentation completeness
   - Hardcoded credentials check

2. Security Assessment:
   - Injection vulnerabilities
   - Authentication mechanisms
   - Hardcoded secrets
   - Secure communication

3. Performance Analysis:
   - Logic efficiency
   - Resource management
   - Database operations
   - Caching implementation

4. Best Practices:
   - Error handling patterns
   - Logging mechanisms
   - Testing coverage
   - Design patterns used

Provide structured analysis in the following format:
{output_format}
"""

def analyze_code(code: str, language: str = "Java") -> dict:
    llm = AzureChatOpenAI(
        azure_deployment=os.environ["AZURE_OPENAI_API_DEPLOYMENT_NAME"],
        api_version=os.environ["AZURE_OPENAI_API_VERSION"],
        temperature=0.1
    )
    
    response = llm.invoke([{
        "role": "system", 
        "content": ANALYSIS_PROMPT.format(
            output_format="{code quality, security, performance, best practices}"
        )
    }])
    
    return response.content