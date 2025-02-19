from setuptools import setup, find_packages

setup(
    name='codeAnalyser',
    version='0.1.0',
    description='A project using LangGraph and Streamlit',
    author='name',
    author_email='email@example.com',
    url='',  # replace with your project's URL
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'langchain',        # Or the specific package you are using for LangGraph
        'streamlit',
        'pandas',           # Add other dependencies as required
        'numpy',
        'requests',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',  # Specify the required Python version
)
