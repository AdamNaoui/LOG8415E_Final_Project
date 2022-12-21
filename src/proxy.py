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
    my_sql_connection = pymysql.connect(host=master["IP"],
                                        port=master["PORT"],
                                        user='adam',  # as defined when set up of the master node instance
                                        password='password',  # as defined when set up of the master node instance
                                        database='sakila',
                                        charset='utf8mb4',
                                        cursorclass=pymysql.cursors.DictCursor)

    SQL_WRITE_OPERATION = "INSERT INTO city (city, country_id, last_update) VALUES ('Paris', 103, '2020-12-12 12:12:12');"

    with my_sql_connection:
        with my_sql_connection.cursor() as cursor:
            cursor.execute(SQL_WRITE_OPERATION)
            result = cursor.fetchone()

    res = "You have reached the master node by using the route (direct).\n You have mutate the database with the following query: " + SQL_WRITE_OPERATION
    for key, value in result.items():
        res += f"{key}: {value}\n"
    return res


@app.route('/random')
def random_endpoint():
    chosen_slave = random.choice(slaves)
    my_sql_connection = pymysql.connect(host=chosen_slave["IP"],
                                        port=chosen_slave["PORT"],  # the port is the one of the ssh tunnel
                                        user='adam',  # as defined when set up of the master node instance
                                        password='password',  # as defined when set up of the master node instance
                                        database='sakila',
                                        charset='utf8mb4',
                                        cursorclass=pymysql.cursors.DictCursor)

    SQL_READ_OPERATION = "SELECT * FROM city LIMIT 5;"
    with my_sql_connection:
        with my_sql_connection.cursor() as cursor:
            cursor.execute(SQL_READ_OPERATION)
            result = cursor.fetchone()

    res = "You have reached the " + chosen_slave[
        "NAME"] + " by using the route (random).\nHere is the result your query: \n\n"

    for key, value in result.items():
        res += f"{key}: {value}\n"
    return res


@app.route('/custom')
def custom_endpoint():
    nodes = [master] + slaves
    min_ping_instance = min(nodes, key=lambda node: get_instance_ping(node["IP"]))

    my_sql_connection = pymysql.connect(host=min_ping_instance["IP"],
                                        port=min_ping_instance["PORT"],  # the port is the one of the ssh tunnel
                                        user='adam',  # as defined when set up of the master node instance
                                        password='password',  # as defined when set up of the master node instance
                                        database='sakila',
                                        charset='utf8mb4',
                                        cursorclass=pymysql.cursors.DictCursor)

    SQL_READ_OPERATION = "SELECT * FROM city LIMIT 5;"
    with my_sql_connection:
        with my_sql_connection.cursor() as cursor:
            cursor.execute(SQL_READ_OPERATION)
            result = cursor.fetchone()

    res = "You have reached the " + min_ping_instance[
        "NAME"] + " by using the route (random).\nHere is the result your query: \n\n"

    for key, value in result.items():
        res += f"{key}: {value}\n"
    return res
