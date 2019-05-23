This document will list the steps to generate the RI pricing for ec2 instances, given a list of EC2 instnaces returned by the AWS cli.
This is done semi-automatically.
The python script will just generate a csv file based on a instance list, and pre-parsed pricing files. The parsing of the pricing file is done by `jq`.

## Prerequiste

You will need a list of instances, with the minimum info needed being the class of the instance.

You will also need the EC2 pricing file, which can be downloaded here : https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/index.json
 (note that it's 600mb).

## Preparing instance list

The instance list was parsed by hand, using `jq`. I just extracted the needed info from the json output of `aws ec2 describe-instance`. The info that I extracted is as follow : 

```json
[
    {
        "instanceID": "i-XXXXX",
        "instanceType": "t2.medium",
        "LaunchTime": "2018-09-04T15:35:21.000Z",
        "tags": [
            {
                "Key": "Name",
                "Value": "XXXXX"
            }
        ]
    }
    , {...}
]
```

If you had/remove fields, the python file generating the csv will have to be changed accordingly.
This file should be named `instances_list.json`.

## Generating pricing files

The actual parsing of the pricing file was done by hand with the help of `jq`. Here are the steps to parse and prepare the pricing list.

### Get all instance types

First, we need to get a list of all the different instance types in the list of instances.

To do this, you can use this `jq` command to get a list of instances types, with a instance list similar to the one I described before :

```bash
jq '.[] | .instanceType' instances_list.json | sort | uniq | tr -d '"' > instances_class
```

### Generate pricing based on classes types

Once we have the instances type list, we can generate pricing files to help speedup the actual pricing generation (as parsing a 600mb file for each instance is pretty slow).

To do so, you can use this bash script : 

```bash
mkdir prices
> prices/instances_class_map
for class in $(cat instances_class)
do
    sku=$(jq '.products[] | if .attributes.location == "US West (Oregon)" and .attributes.instanceType == "'$class'" and .attributes.preInstalledSw == "NA" and .attributes.tenancy == "Shared" and .attributes.operatingSystem == "Linux" then . else empty end | .attributes.instancesku // empty' pricing_ec2.json | uniq | tr -d '"')
    echo "$class:$sku" >> prices/instances_class_map
    jq '[.terms.OnDemand["'$sku'"][], .terms.Reserved["'$sku'"][] | {termLength: .termAttributes.LeaseContractLength, termOffering: .termAttributes.OfferingClass, termPurchaseOption: .termAttributes.PurchaseOption, price: .priceDimensions}]' pricing_ec2.json > prices/$sku
done
```

This script makes a few assumption : 
- The region of the instance is `us-west-2` (although it can be changed by changing the `.attributes.location == "US West (Oregon)"` condition)
- There is no preinstalled software on the instance
- It is a Shared instance (and not for example Dedicated)
- The OS is Linux (and not something like RHEL or Windows with licencing fees)

## Generating CSV file

Once the pricing files are generated, you can run the `parse_ri.py` file (python3), and it will generate you a CSV file, as `report.csv`.

Right now the `Savings` percentages are not inserted in the CSV file, and should be added by hand in the Excel/GDocs sheet. 