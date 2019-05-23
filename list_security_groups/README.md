This tool will list all the security groups of the account(s), accross all regions, giving for each SG those infos : 
- Account Name
- Region
- VPC ID
- SG ID
- TAGS
- A list of all rules :
    - Ingress protocol
    - Ingress port
    - Ingress source (either CIDR ips, or SG ids)
    - Egress protocol
    - Egress port
    - Egress source (either CIDR ips, or SG ids)

The dependencies are :
- Python 2
- boto3

To launch it, just run `python2 list_sg.py --profile [PROFILE_NAME, PROFILE_NAME, ...]`

The report will be saved as `report.csv`