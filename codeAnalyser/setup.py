'''
This file provided is a setup.py file, which is used for packaging and distributing a Python project. 
The setup.py file is read by tools like pip and setuptools to install your package and its dependencies.
'''

from setuptools import setup, find_packages

setup(
    name='codeAnalyser',
    version='0.1.0',
    description='A project using LangGraph(Model) FAST-API(endpoint) and Streamlit(UI)',
    author='#name',
    author_email='#email@example.com',
    url='',  
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'streamlit',
        'pandas',
        'numpy',
        'requests',
        'fastapi',
        'pydantic',
        'typing',
        'langchain',
        'langchian_community',
        'langgraph',
        'langchain_groq',
        'uvicorn',
    ],
    classifiers=[
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved ::  License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',  # Specify the required Python version
)
