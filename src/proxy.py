#!/usr/bin/python
from flask import Flask
from pythonping import ping

from src.proxy_constants import MASTER_IP, FIRST_SLAVE_IP, SECOND_SLAVE_IP, THIRD_SLAVE_IP

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


master = {"name": "Master node", "ip": MASTER_IP, "port": 3306}
first_slave = {"name": "Slave node 1", "ip": FIRST_SLAVE_IP, "port": 3307}
second_slave = {"name": "Slave node 2", "ip": SECOND_SLAVE_IP, "port": 3308}
third_slave = {"name": "Slave node 3", "ip": THIRD_SLAVE_IP, "port": 3309}


