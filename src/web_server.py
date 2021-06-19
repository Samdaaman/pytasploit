from flask import Flask
import os
app = Flask(__name__)


@app.route('/pyterpreter')
def get_pyterpreter():
    os.system()
