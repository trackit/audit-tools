This tool list all the Elastic Load Balancers (v1 & v2) across all regions, and across all profiles that you pass as arguments.

It will give those info for each Load Balancer : 

- Account
- Region
- Type
- ARN (only for elbv2)
- Hosted Zone ID
- VPC ID
- LB Name
- Tags
- Instances
- Listeners
- Security Groups
- Scheme

The dependencies are :
- Python 2
- boto3

To launch it, just run `python2 list-elbs.py --profile [PROFILE_NAME, PROFILE_NAME, ...]`.

The output file will be saved as `report.csv`, or you can change it with the `-o` argument.