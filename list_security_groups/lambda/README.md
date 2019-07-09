# Automated reporting with Lambda

## Setup

### Create Lambda function

Create a lambda function with the code inside `lambda.py`. Use python2.7

Change the ENV var, it will be used as a prefix in your s3 bucket

Change the BUCKET var, it should match your S3 target bucket

### Attach the following role to your lambda

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*",
            "Effect": "Allow"
        },
        {
            "Action": [
                "ec2:DescribeInstances",
                "ec2:DescribeInstanceStatus",
                "ec2:StopInstances",
                "ec2:StartInstances",
                "ec2:RunInstances"
            ],
            "Resource": "*",
            "Effect": "Allow"
        },
        {
            "Effect": "Allow",
            "Action": "sts:DecodeAuthorizationMessage",
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": "iam:PassRole",
            "Resource": "*"
        }
    ]
}
```

### Create a role for you ec2 instances

Attach Readonly policy and the following policy

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "s3:PutAccountPublicAccessBlock",
                "s3:GetAccountPublicAccessBlock",
                "s3:ListAllMyBuckets",
                "s3:ListJobs",
                "s3:CreateJob",
                "s3:HeadBucket",
                "s3:PutObject"
            ],
            "Resource": "*"
        }
    ]
}
```

### Cloudwatch trigger

Add a CloudWatch Events trigger to your lambda with the schedule you would like (1st of the month for example)
