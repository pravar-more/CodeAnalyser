import os
from typing import Dict

class TechStackDetector:
    def __init__(self, project_root: str):
        self.project_root = project_root
        
    def detect_tech_stack(self) -> Dict[str, list]:
        return {
            "frontend": self._detect_frontend(),
            "backend": self._detect_backend(),
            "database": self._detect_database(),
            "build_tools": self._detect_build_tools()
        }
        
    def _detect_frontend(self) -> list:
        frameworks = []
        indicators = {
            "React": ["package.json", "react"],
            "Angular": ["angular.json", "angular"],
            "Vue": ["package.json", "vue"],
        }
        
        for framework, [file, keyword] in indicators.items():
            if os.path.exists(os.path.join(self.project_root, file)):
                frameworks.append(framework)
        return frameworks
        
    def _detect_backend(self) -> list:
        frameworks = []
        if os.path.exists(os.path.join(self.project_root, "pom.xml")):
            with open(os.path.join(self.project_root, "pom.xml")) as f:
                content = f.read()
                if "spring-boot" in content:
                    frameworks.append("Spring Boot")
                if "micronaut" in content:
                    frameworks.append("Micronaut")
        return frameworks
        
    def _detect_database(self) -> list:
        databases = []
        db_indicators = {
            "PostgreSQL": ["postgresql", "postgres"],
            "MySQL": ["mysql"],
            "MongoDB": ["mongodb"],
        }
        
        if os.path.exists(os.path.join(self.project_root, "pom.xml")):
            with open(os.path.join(self.project_root, "pom.xml")) as f:
                content = f.read().lower()
                for db, keywords in db_indicators.items():
                    if any(keyword in content for keyword in keywords):
                        databases.append(db)
        return databases
        
    def _detect_build_tools(self) -> list:
        tools = []
        if os.path.exists(os.path.join(self.project_root, "pom.xml")):
            tools.append("Maven")
        if os.path.join(self.project_root, "build.gradle"):
            tools.append("Gradle")
        return tools