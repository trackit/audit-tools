from datetime import date
import boto3

ENV="stg"
REGION = 'us-west-2'

today = date.today()

AMI = 'ami-07669fc90e6e6cc47'
INSTANCE_TYPE = 't3.small'
DATE = today.strftime("%Y-%d-%b")
EC2 = boto3.client('ec2', region_name=REGION)
BUCKET = 'mydestinationbucket'

def lambda_to_ec2(event, context):
    init_script = """#!/bin/bash
sudo yum update -y
sudo yum install -y git python2-pip
cd /home/ec2-user
git clone -b ec2_role https://github.com/trackit/aws-audit-tools.git
cd aws-audit-tools/list_security_groups
pip install boto3
python list_sg.py --profile default
aws s3 cp report.csv s3://""" + BUCKET + """/""" + ENV + """/report_""" + DATE + """.csv
shutdown -h now
"""

    print 'Running script:'
    print init_script

    instance = EC2.run_instances(
        ImageId=AMI,
        InstanceType=INSTANCE_TYPE,
        MinCount=1,
        MaxCount=1,
        InstanceInitiatedShutdownBehavior='terminate',
        UserData=init_script,
        IamInstanceProfile={
            'Name': 'sg-report-ec2'
        }
    )

    print "New instance created."
    instance_id = instance['Instances'][0]['InstanceId']
    print instance_id

    return instance_id
