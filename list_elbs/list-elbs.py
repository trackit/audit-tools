import boto3
import botocore
import csv
import argparse
import ConfigParser
import os
import re

def get_tags_formatted(tags):
    if tags == "":
        return "" 
    res = ""
    for elem in tags:
        res += "{}={}, ".format(elem["Key"], elem["Value"])
    return res[:-2]

def get_tags_elbv1(client, lb_name):
    tags = client.describe_tags(
        LoadBalancerNames=[
            lb_name,
        ],
    )
    return get_tags_formatted(tags["TagDescriptions"][0]["Tags"])

def get_tags_elbv2(client, lb_arn):
    tags = client.describe_tags(
        ResourceArns=[
            lb_arn,
        ],
    )
    return get_tags_formatted(tags["TagDescriptions"][0]["Tags"])

def get_elbv1_ips(session, regions, account):
    res = []
    for region in regions:
        client = session.client('elb', region_name=region)
        load_balancers = client.describe_load_balancers()
        for load_balancer in load_balancers["LoadBalancerDescriptions"]:
            res.append({
                "Account": account,
                "Region": region,
                "Hosted Zone ID": load_balancer["CanonicalHostedZoneNameID"],
                "VPC ID": load_balancer["VPCId"] if "VPCId" in load_balancer else "",
                "LB Name": load_balancer["LoadBalancerName"],
                "Tags": get_tags_elbv1(client, load_balancer["LoadBalancerName"]),
                "Instances": ', '.join(x["InstanceId"] for x in load_balancer["Instances"]),
                "Listeners": ', '.join(
                    "{{protocol: {0}, lb port: {1}, instance port: {2}, instance protocol: {3}}}".format(
                        x['Listener']['Protocol'],
                        x['Listener']['LoadBalancerPort'],
                        x['Listener']['InstancePort'],
                        x['Listener']['InstanceProtocol']
                    ) for x in load_balancer['ListenerDescriptions']
                ),
                "Security Groups": ', '.join(x for x in load_balancer['SecurityGroups']),
                "Scheme": load_balancer["Scheme"],
                "Type": "classic"
            })
    return res

def get_instances_elbv2(client, lb_arn):
    target_groups_arn = [x['TargetGroupArn'] for x in client.describe_target_groups(
        LoadBalancerArn=lb_arn
    )["TargetGroups"]]
    instances = []
    for target_group in target_groups_arn:
        target_group_info = client.describe_target_health(
            TargetGroupArn=target_group
        )
        for target in target_group_info["TargetHealthDescriptions"]:
            instances.append(
                "{{id: {0}, port: {1}}}".format(target["Target"]["Id"], target["Target"]["Port"])
            )
    return ", ".join(instances)

def get_listeners_elbv2(client, lb_arn):
    listeners = client.describe_listeners(
        LoadBalancerArn=lb_arn
    )['Listeners']
    listeners_ret = []
    for listener in listeners:
        listeners_ret.append(
            "{{protocol: {0}, port: {1}}}".format(listener["Protocol"], listener["Port"])
        )
    return ", ".join(listeners_ret)

def get_elbv2_ips(session, regions, account):
    res = []
    for region in regions:
        client = session.client('elbv2', region_name=region)
        load_balancers = client.describe_load_balancers()
        for load_balancer in load_balancers["LoadBalancers"]:
            res.append({
                "Account": account,
                "Region": region,
                "ARN": load_balancer["LoadBalancerArn"],
                "Hosted Zone ID": load_balancer["CanonicalHostedZoneId"],
                "VPC ID": load_balancer["VpcId"],
                "LB Name": load_balancer["LoadBalancerName"],
                "Tags": get_tags_elbv2(client, load_balancer["LoadBalancerArn"]),
                "Instances": get_instances_elbv2(client, load_balancer["LoadBalancerArn"]),
                "Listeners": get_listeners_elbv2(client, load_balancer["LoadBalancerArn"]),
                "Security Groups": ", ".join(load_balancer["SecurityGroups"]),
                "Scheme": load_balancer["Scheme"],
                "Type": load_balancer["Type"]
            })
    return res

def get_regions(session):
    client = session.client('ec2')
    regions = client.describe_regions()
    return [
        region['RegionName']
        for region in regions['Regions']
    ]

def generate_csv(data, args, header_name):
    filename = "report.csv"
    if args['o']:
        filename = args['o']
    with open(filename, 'wb') as file:
        writer = csv.DictWriter(file, header_name)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

def init():
    config_path = os.environ.get('HOME') + "/.aws/credentials"
    parser = ConfigParser.ConfigParser()
    parser.read(config_path)
    if parser.sections():
        return parser.sections()
    return []

def main():
    data = []
    parser = argparse.ArgumentParser(description="Analyse reserved instances")
    parser.add_argument("--profile", nargs="+", help="Specify AWS profile(s) (stored in ~/.aws/credentials) for the program to use")
    parser.add_argument("-o", nargs="?", help="Specify output csv file")
    parser.add_argument("--profiles-all", nargs="?", help="Run it on all profile")
    aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    aws_region = os.environ.get('AWS_DEFAULT_REGION')
    args = vars(parser.parse_args())
    if 'profiles-all' in args:
        keys = init()
    elif 'profile' in args and args['profile']:
        keys = args['profile']
    else:
        keys = init()
    for key in keys:
        print 'Processing %s...' % key
        try:
            if aws_access_key and aws_secret_key and aws_region:
                session = boto3.Session(aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=aws_region)
            else:
                session = boto3.Session(profile_name=key)
            regions = get_regions(session)
            data += get_elbv1_ips(session, regions, key)
            data += get_elbv2_ips(session, regions, key)
        except botocore.exceptions.ClientError, error:
            print error
    generate_csv(data, args, ["Account", "Region", "Type", "ARN", "Hosted Zone ID", "VPC ID", "LB Name", "Tags", "Instances", "Listeners", "Security Groups", "Scheme"])


if __name__ == '__main__':
    main()
