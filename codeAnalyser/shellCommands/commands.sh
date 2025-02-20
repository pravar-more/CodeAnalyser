#
python -m venv venv
.\venv\Scripts\activate         #for windows
source venv/bin/activate        #for linux

#cd $HOME/codeAnalyser/docs/
cd ./codeAnalyser/docs/
pip install -r requirements.txt

cd ./codeAnalyser
python setup.py install

cd ./codeAnalyser/streamlit_app
streamlit run .\app.py
deactivate