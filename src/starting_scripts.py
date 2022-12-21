USER_DATA_STAND_ALONE_SERVER = """#!/bin/bash
sudo apt update  && \
sudo apt install mysql-server -y  && \
sudo systemctl start mysql.service && \
sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'password';" && \
wget  https://downloads.mysql.com/docs/sakila-db.tar.gz && \
tar -xzf sakila-db.tar.gz && \
mysql -u root --password=password -e "SOURCE sakila-db/sakila-schema.sql" && \
mysql -u root --password=password -e "SOURCE sakila-db/sakila-data.sql"  && \
sudo mysql -u root --password=password -e "CREATE USER 'adam'@'%' IDENTIFIED BY 'password';"  && \
sudo mysql -u root --password=password -e "GRANT ALL PRIVILEGES ON *.* TO 'adam'@'%' WITH GRANT OPTION;"  && \
sudo mysql -u root --password=password -e "FLUSH PRIVILEGES;" && \
sudo apt install sysbench -y
"""

USER_DATA_MASTER = """#!/bin/bash
sudo apt-get update && \
sudo apt-get install -y libncurses5 libaio1 libmecab2 && \
mkdir -p /opt/mysqlcluster/home && \
mkdir -p /var/lib/mysqlcluster && \
wget --progress=bar:force:noscroll https://dev.mysql.com/get/Downloads/MySQL-Cluster-7.6/mysql-cluster-community-management-server_7.6.6-1ubuntu18.04_amd64.deb && \
dpkg -i mysql-cluster-community-management-server_7.6.6-1ubuntu18.04_amd64.deb && \
wget --progress=bar:force:noscroll http://dev.mysql.com/get/Downloads/MySQL-Cluster-7.2/mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz && \
tar -xf mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz && \
mv mysql-cluster-gpl-7.2.1-linux2.6-x86_64 mysqlc && \
echo "alias ndb_mgm=/home/ubuntu/mysqlc/bin/ndb_mgm" >> /home/ubuntu/.profile && \
sudo apt install sysbench -y
"""

USER_DATA_SLAVES = """#!/bin/bash
sudo apt-get update && \
sudo apt-get install -y libncurses5 libclass-methodmaker-perl && \
mkdir -p /opt/mysqlcluster/home && \
mkdir -p /var/lib/mysqlcluster && \
cd /opt/mysqlcluster/home && \
wget --progress=bar:force:noscroll https://dev.mysql.com/get/Downloads/MySQL-Cluster-7.6/mysql-cluster-community-data-node_7.6.6-1ubuntu18.04_amd64.deb && \
dpkg -i mysql-cluster-community-data-node_7.6.6-1ubuntu18.04_amd64.deb  && \
sudo mkdir -p /opt/mysqlcluster/deploy/mysqld_data
"""

USER_DATA_PROXY = """#!/bin/bash
sudo apt update && \
sudo apt install -y python3 python3-flask python3-pip && \
sudo pip3 install pymysql sshtunnel pythonping
"""
