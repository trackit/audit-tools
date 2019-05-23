This tool lists all the publicly exposed (to 0.0.0.0/0) ports on EC2 instances for one or mutiple accounts, across all regions.

The dependencies are :
- Python 2
- boto3

To launch it, just run `python2 check-ec2-publicly-exposed.py --profile AWSProfileName`.

The output file will be saved as `report.csv`, or you can change it with the `-o` argument.