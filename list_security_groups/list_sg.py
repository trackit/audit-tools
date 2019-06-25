import boto3
import argparse
import sys
import csv

def format_security_group_output(sg):
    res = []
    for rule in sg:
        port = "-1"
        if "FromPort" in rule:
            if rule["FromPort"] == rule["ToPort"]:
                port = str(rule["FromPort"])
            else:
                port = "{}-{}".format(rule["FromPort"], rule["ToPort"])
        ip_ranges = ""
        for ip_range in rule["IpRanges"]:
            ip_ranges += "{}, ".format(ip_range["CidrIp"])
        if ip_ranges == "":
            for sg_user in rule["UserIdGroupPairs"]:
                ip_ranges += "{}:{}, ".format(sg_user["UserId"], sg_user["GroupId"])
        if ip_ranges != "":
            ip_ranges = ip_ranges[:-2]
        res.append({
            "port": port,
            "source": ip_ranges,
            "protocol": rule["IpProtocol"]
        })
    return res

def formatted_sg_to_string(sg):
    res = ""
    for elem in sg:
        res += "Protocol: {}, port: {}, source: {}\n".format(elem["protocol"], elem["port"], elem["ipRange"])
    return res[:-1]

def format_tags(tags):
    res = ""
    if tags is None:
        return res
    for elem in tags:
        res += "{}={}, ".format(elem["Key"], elem["Value"])
    return res[:-2]

def get_region(session):
    ec2 = session.client('ec2')
    regions = ec2.describe_regions()
    for region in regions['Regions']:
        yield region['RegionName']

def get_vpc_and_sg(ec2_ressources):
    for vpc in ec2_ressources.vpcs.all():
        for security_group in vpc.security_groups.all():
            yield vpc, security_group

def get_ip_permissions_vpc_and_sg(ec2_ressources, ip_permission_type):
    for vpc, security_group in get_vpc_and_sg(ec2_ressources):
        yield vpc, security_group, security_group.ip_permissions_egress, security_group.ip_permissions, security_group.tags

def get_sg(profile, data=None):
    ret = []
    for region in get_region(boto3.Session()):
        ec2_ressources = boto3.Session(region_name=region).resource('ec2')
        for vpc, security_group, ip_permission_egress, ip_permission_ingress, tags in get_ip_permissions_vpc_and_sg(ec2_ressources, ""):
            i = 0
            ip_permission_egress = format_security_group_output(ip_permission_egress)
            ip_permission_ingress = format_security_group_output(ip_permission_ingress)
            while i < len(ip_permission_egress) or i < len(ip_permission_ingress):
                buff = {
                    "Account": profile,
                    "VPC Id": vpc.id,
                    "SG Id": security_group.id,
                    "tags": format_tags(tags),
                    "Region": region
                }
                if i < len(ip_permission_egress):
                    buff["e_protocol"] = ip_permission_egress[i]["protocol"]
                    buff["e_port"] = ip_permission_egress[i]["port"]
                    buff["e_source"] = ip_permission_egress[i]["source"]
                if i < len(ip_permission_ingress):
                    buff["i_protocol"] = ip_permission_ingress[i]["protocol"]
                    buff["i_port"] = ip_permission_ingress[i]["port"]
                    buff["i_source"] = ip_permission_ingress[i]["source"]
                ret.append(buff)
                i += 1
    return ret

def main():
    parser = argparse.ArgumentParser(description="Tool to list security groups")
    parser.add_argument("--profile", nargs="+", help="Specify AWS profile(s) (stored in ~/.aws/credentials) for the program to use")
    args = vars(parser.parse_args())
    data = []
    for keys in args["profile"]:
        print "Processing {} ...".format(keys)
        data.extend(get_sg(keys))
    with open('report.csv', 'w') as out:
        writer = csv.DictWriter(out, ["Account", "Region", "VPC Id", "SG Id", "tags", "i_protocol", "i_port", "i_source", "e_protocol", "e_port", "e_source"])
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    main()
