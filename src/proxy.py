#!/usr/bin/python
import random
from flask import Flask
from pythonping import ping
from sshtunnel import SSHTunnelForwarder
from src.proxy_constants import MASTER_IP, FIRST_SLAVE_IP, SECOND_SLAVE_IP, THIRD_SLAVE_IP
import pymysql.cursors


def get_instance_ping(host):
    ping_result = ping(target=host, timeout=3, count=10)
    return ping_result.rtt_avg_ms


def get_formated_content(results):
    formatted_res = "<table>"
    keys = []
    for result in results:
        if not keys:
            keys = result.keys()
            formatted_res += "<tr>"
            for key in keys:
                formatted_res += f"<th>{key}</th>"
            formatted_res += "</tr>"
        formatted_res += "<tr>"

        for key, value in result.items():
            formatted_res += f"<td>{value}</td>"
        formatted_res += "</tr>"
    formatted_res += "</table>"
    return formatted_res


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


@app.route('/direct')
def direct_hit():
    # forward the request directly to the master
    connection = pymysql.connect(host=master["IP"],
                                 port=master["PORT"],
                                 user='adam',
                                 password='password',
                                 database='sakila',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    with connection:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM city LIMIT 5;"
            cursor.execute(sql)
            results = cursor.fetchall()

    formatted_res = get_formated_content(results)

    return """
        <h1> You're querying Master node</h1><h2>Because of {_ROUTE_TYPE_} route type</h2>
        {_CONTENT_}""".format(_ROUTE_TYPE_="Normal",
                              _CONTENT_=formatted_res)


@app.route('/random')
def random_endpoint():
    chosen_slave = random.choice(slaves)
    connection = pymysql.connect(host="127.0.0.1",
                                 port=chosen_slave["PORT"],
                                 user='adam',
                                 password='password',
                                 database='sakila',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    with connection:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM city LIMIT 10"
            cursor.execute(sql)

            results = cursor.fetchall()
    formatted_res = get_formated_content(results)
    return """
        <h1> You're querying {_NAME_} node</h1><h2>Because of {_ROUTE_TYPE_}</h2>
        {_CONTENT_}""".format(_ROUTE_TYPE_="Random", _NAME_=chosen_slave["name"],
                              _CONTENT_=formatted_res)


@app.route('/custom')
def custom_endpoint():
    nodes = [master] + slaves
    min_ping_instance = min(nodes, key=lambda node: get_instance_ping(node["IP"]))

    # ping the endpoints, and forward to the right one
    connection = pymysql.connect(host=min_ping_instance["IP"],
                                 port=min_ping_instance["PORT"],
                                 user='adam',
                                 password='password',
                                 database='sakila',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    with connection:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM city LIMIT 10"
            cursor.execute(sql)
            results = cursor.fetchall()
    formatted_res = get_formated_content(results)

    return """
            <h1> You're querying {_NAME_} node</h1><h2>Because of {_ROUTE_TYPE_}</h2>
            {_CONTENT_}""".format(_ROUTE_TYPE_="Custom", _NAME_=min_ping_instance["name"],
                                  _CONTENT_=formatted_res)
