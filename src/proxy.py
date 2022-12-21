#!/usr/bin/python
from flask import Flask
from pythonping import ping

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


def get_instance_ping(host):
    ping_result = ping(target=host, timeout=3, count=10)
    return ping_result.rtt_avg_ms
