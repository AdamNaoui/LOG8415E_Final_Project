#!/usr/bin/python
from flask import Flask

app = Flask(__name__)


@app.route('/normal')
def normal_endpoint():
    pass


@app.route('/custom')
def custom_endpoint():
    pass


@app.route('/random')
def random_endpoint():
    pass
