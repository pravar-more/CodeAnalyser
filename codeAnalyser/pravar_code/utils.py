# langgraph/utils.py
import os
from git import Repo
from collections import defaultdict
import pandas as pd

def clone_repo(repo_url, clone_dir="temp_repo"):
    if os.path.exists(clone_dir):
        os.system(f"rm -rf {clone_dir}")
    Repo.clone_from(repo_url, clone_dir)
    return clone_dir

def analyze_repo(clone_dir):
    file_counts = defaultdict(int)
    language_counts = defaultdict(int)
    
    for root, dirs, files in os.walk(clone_dir):
        for file in files:
            file_path = os.path.join(root, file)
            file_extension = os.path.splitext(file)[1]
            file_counts[file_extension] += 1
            language_counts[file_extension] = file_extension_to_language(file_extension)
    
    file_counts_df = pd.DataFrame(list(file_counts.items()), columns=['File Type', 'Count'])
    languages_df = pd.DataFrame(list(language_counts.items()), columns=['Language', 'Count'])
    
    return file_counts_df, languages_df

def file_extension_to_language(extension):
    language_map = {
        '.py': 'Python',
        '.java': 'Java',
        '.js': 'JavaScript',
        '.html': 'HTML',
        '.css': 'CSS',
        # Add more mappings as needed
    }
    return language_map.get(extension, 'Unknown')
