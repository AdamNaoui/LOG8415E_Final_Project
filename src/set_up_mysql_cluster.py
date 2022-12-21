import boto3
import starting_scripts

# Set up the AWS client for EC2
ec2 = boto3.client('ec2')

# Create a security group to allow MySQL traffic
mysql_security_group = ec2.create_security_group(
    GroupName='mysql-cluster',
    Description='Security group for MySQL cluster'
)
mysql_security_group_id = mysql_security_group['GroupId']
ec2.authorize_security_group_ingress(
    GroupId=mysql_security_group_id,
    IpPermissions=[{
        'IpProtocol': 'tcp',
        'FromPort': 3306,
        'ToPort': 3306,
        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
    }]
)

# Create THREE t2.micro instances for the three slaves
slaves = ec2.run_instances(
    UserData=starting_scripts.USER_DATA_SLAVES,
    ImageId='ami-0a6b2839d44d781b2',
    InstanceType='t2.micro',
    MinCount=3,
    MaxCount=3,
    SecurityGroupIds=[mysql_security_group_id],
    KeyName='my_key_pair'
)
# Wait for the instances to be in the 'running' state
slaves_id = [slave['InstanceId'] for slave in slaves['Instances']]
ec2.get_waiter('instance_running').wait(InstanceIds=slaves_id)

# Get the public IP addresses of the instances
slaves_info = ec2.describe_instances(InstanceIds=slaves_id)
slaves_public_ips = [slave['PublicIpAddress'] for slave in slaves_info['Reservations'][0]['Instances']]

with open('IPs.txt', 'w') as f:
    f.write('\nSlave1IP: ' + slaves_public_ips[1])
    f.write('\nSlave2IP: ' + slaves_public_ips[2])
    f.write('\nSlave3IP: ' + slaves_public_ips[3])

# Create One t2.micro instances for the master
master_instance = ec2.run_instances(
    UserData=starting_scripts.USER_DATA_MASTER,
    ImageId='ami-0a6b2839d44d781b2',
    InstanceType='t2.micro',
    MinCount=1,
    MaxCount=1,
    SecurityGroupIds=[mysql_security_group_id],
    KeyName='my_key_pair'
)

master_id = [master['InstanceId'] for master in master_instance['Instances']]
ec2.get_waiter('instance_running').wait(InstanceIds=master_id)

# Get the public IP addresses of the master
master_info = ec2.describe_instances(InstanceIds=master_id)
master_public_ip = [master['PublicIpAddress'] for master in master_info['Reservations'][0]['Instances']]

with open('IPs.txt', 'w') as f:
    f.write('\nMasterIP: ' + master_public_ip[0])

# Create One t2.micro instances for the master
proxy_instance = ec2.run_instances(
    UserData=starting_scripts.USER_DATA_PROXY,
    ImageId='ami-0a6b2839d44d781b2',
    InstanceType='t2.large',
    MinCount=1,
    MaxCount=1,
    SecurityGroupIds=[mysql_security_group_id],
    KeyName='my_key_pair'
)

proxy_id = [proxy['InstanceId'] for proxy in proxy_instance['Instances']]
ec2.get_waiter('instance_running').wait(InstanceIds=proxy_id)

# Get the public IP addresses of the proxy
proxy_info = ec2.describe_instances(InstanceIds=proxy_id)
proxy_public_ip = [proxy['PublicIpAddress'] for proxy in proxy_info['Reservations'][0]['Instances']]

with open('IPs.txt', 'w') as f:
    f.write('\nMasterIP: ' + proxy_public_ip[0])
