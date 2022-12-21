#!/usr/bin/python
from flask import Flask
from pythonping import ping
from sshtunnel import SSHTunnelForwarder
from src.proxy_constants import MASTER_IP, FIRST_SLAVE_IP, SECOND_SLAVE_IP, THIRD_SLAVE_IP


def get_instance_ping(host):
    ping_result = ping(target=host, timeout=3, count=10)
    return ping_result.rtt_avg_ms


master = {"NAME": "Master node", "IP": MASTER_IP, "PORT": 3306}
first_slave = {"NAME": "Slave node 1", "IP": FIRST_SLAVE_IP, "PORT": 3307}
second_slave = {"NAME": "Slave node 2", "IP": SECOND_SLAVE_IP, "PORT": 3308}
third_slave = {"NAME": "Slave node 3", "IP": THIRD_SLAVE_IP, "PORT": 3309}

slaves = [first_slave, second_slave, third_slave]

# creating ssh tunnels form slaves to master
for slave in slaves:
    tunnel = SSHTunnelForwarder(
        (slave["IP"], 22),
        ssh_pkey="/home/ubuntu/private_key_PROJET_KEY.pem",
        ssh_username="ubuntu",
        allow_agent=False,
        local_bind_address=('127.0.0.1', slave["PORT"]),
        remote_bind_address=(master["IP"], master["PORT"]))
    tunnel.start()

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
