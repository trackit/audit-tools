import json
import pprint
import csv

fieldnames = [
    "id",
    "type",
    "launch date",
    "tags",
    'On Demand cost', 
    'standard 1yr No Upfront cost', 
    'savings',
    'standard 1yr Partial Upfront cost', 
    'savings',
    'standard 1yr All Upfront cost', 
    'savings',
    'convertible 1yr No Upfront cost', 
    'savings',
    'convertible 1yr Partial Upfront cost', 
    'savings',
    'convertible 1yr All Upfront cost', 
    'savings',
    'standard 3yr No Upfront cost', 
    'savings',
    'standard 3yr Partial Upfront cost', 
    'savings',
    'standard 3yr All Upfront cost', 
    'savings',
    'convertible 3yr No Upfront cost', 
    'savings',
    'convertible 3yr Partial Upfront cost', 
    'savings',
    'convertible 3yr All Upfront cost',
    'savings'
]


hours_in_year = 365 * 24

def parse_instance_class():
    ret = {}
    with open("prices/instances_class_map", 'r') as instance_class:
        for line in instance_class:
            elems = line.split(':')
            ret[elems[0]] = elems[1].rstrip()
    return ret

def getRiPricePerMonth(elem):
    if elem["termPurchaseOption"] == "No Upfront":
        upfront = 0
    else:
        upfront = [x["pricePerUnit"]["USD"] for key, x in elem["price"].items() if x["unit"] == "Quantity"][0]
    hourlyRate = [x["pricePerUnit"]["USD"] for key, x in elem["price"].items() if x["unit"] == "Hrs"][0]
    if elem["termLength"] == "1yr":
        hoursNb = hours_in_year
        monthNb = 12
    else:
        hoursNb = hours_in_year * 3
        monthNb = 3 * 12
    totalPrice = float(hoursNb) * float(hourlyRate) + float(upfront)
    pricePerMonth = float(totalPrice) / float(monthNb)
    return round(pricePerMonth, 2), "{offering} {length} {option}".format(
        offering=elem["termOffering"],
        length=elem["termLength"],
        option=elem["termPurchaseOption"]
    )

def getODPricePerMonth(elem):
    hourlyRate = [x["pricePerUnit"]["USD"] for key, x in elem["price"].items()][0]
    pricePerMonth = float(hourlyRate) * float(hours_in_year) / float(12)
    return round(pricePerMonth, 2), "On Demand"

def getPrices(sku):
    with open('prices/{sku}'.format(sku=sku), 'r') as price_input:
        prices = json.load(price_input)
    price_list = []
    for price in prices:
        if price["termLength"] is None:
            monthly_price, description = getODPricePerMonth(price)
        else:
            monthly_price, description = getRiPricePerMonth(price)
        price_list.append({
            "price": monthly_price,
            "type": description
        })
    return price_list

def generate_tags(tags):
    if tags is None:
        return ""
    tag_str = ""
    tags.sort(key=lambda x: x["Value"])
    for elem in tags:
        tag_str += "{key}={value},".format(
            key=elem["Key"],
            value=elem["Value"]
        )
    return tag_str[:-1]


def create_cost_object(prices):
    cost_obj = {}
    for elem in prices:
        cost_obj["{} cost".format(elem["type"])] = elem["price"]
    return cost_obj

def main():
    with open('instances_list.json', 'r') as instances_raw:
        instances = json.load(instances_raw)
    with open('report.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, restval="")
        writer.writeheader()
        instance_classes = parse_instance_class()
        for instance in instances:
            instance_sku = instance_classes[instance["instanceType"]]
            price_list = getPrices(instance_sku)
            res_dict = create_cost_object(price_list)
            res_dict["id"] = instance["instanceID"]
            res_dict["type"] = instance["instanceType"]
            res_dict["launch date"] = instance["LaunchTime"].split('T')[0]
            res_dict["tags"] = generate_tags(instance["tags"])
            writer.writerow(res_dict)

if __name__ == "__main__":
    main()