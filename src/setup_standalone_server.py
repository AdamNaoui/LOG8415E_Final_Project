import boto3
import subprocess

# Create an EC2 client
ec2 = boto3.client('ec2')

# Create a key pair
key_pair = ec2.create_key_pair(KeyName='my_key_pair')
with open('my_key_pair.pem', 'w') as f:
    f.write(key_pair['KeyMaterial'])

# Create a security group
security_group = ec2.create_security_group(
    GroupName='my_security_group',
    Description='My security group'
)

# Add a rule to the security group to allow incoming SSH connections
ec2.authorize_security_group_ingress(
    GroupId=security_group['GroupId'],
    IpPermissions=[{
        'IpProtocol': 'tcp',
        'FromPort': 22,
        'ToPort': 22,
        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
    }]
)

# Launch an EC2 instance
instance = ec2.run_instances(
    UserData=open('./starting_scripts/stand_alone_server_starting_script.sh').read(),
    ImageId='ami-0a6b2839d44d781b2',  # Ubuntu 20.04 AMI
    InstanceType='t2.micro',
    KeyName='my_key_pair',
    SecurityGroupIds=[security_group['GroupId']],
    MinCount=1,
    MaxCount=1
)

# Get the instance's public IP address
# wait until instance is running
instance_id = instance['Instances'][0]['InstanceId']
ec2.get_waiter('instance_running').wait(InstanceIds=[instance_id])
instance_info = ec2.describe_instances(InstanceIds=[instance_id])
public_ip_address = instance_info['Reservations'][0]['Instances'][0]['PublicIpAddress']

with open('IPS.text', 'w') as f:
    f.write('StandAloneServerIP: ' + public_ip_address)

rc = subprocess.call("chmod 600 my_key_pair.pem", shell=True)

# print correct command ton ssh
print("ssh -i my_key_pair.pem ubuntu@" + public_ip_address)
