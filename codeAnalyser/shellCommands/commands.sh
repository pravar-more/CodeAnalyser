#
python -m venv venv
.\venv\Scripts\activate         #for windows
source venv/bin/activate        #for linux


pip install -r requirements.txt

python setup.py install

deactivate