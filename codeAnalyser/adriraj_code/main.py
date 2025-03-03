import os

def main():
    os.environ['STREAMLIT_SERVER_ADDRESS'] = '127.0.0.1'

    os.system("streamlit run ui.py")

if __name__ == "__main__":
    main()