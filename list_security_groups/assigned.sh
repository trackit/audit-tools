#!/bin/bash

i=0
while read line
do
  line=$(echo  $line | tr -d '\r')
  if [ $i -eq 0 ]
  then
    echo $line,assigned
  else
    REGION=$(echo $line | cut -d',' -f2 | tr -d '\r')
    SG=$(echo $line | cut -d',' -f4 | tr -d '\r')
    ASSOCIATIONS=$(aws ec2 describe-network-interfaces --filters Name=group-id,Values=$SG --region $REGION --output json | jq ".NetworkInterfaces[]|.Attachment.InstanceId")
    #   RESULT="$ASSOCIATIONS"
    line=$(echo  $line | tr -d '\r')
    ASSOCIATIONS=$(echo  $ASSOCIATIONS | tr -d '\r')
    if [ -z "$ASSOCIATIONS" ]
    then
        ASSOCIATIONS="unassigned"
    fi
    echo $line,$ASSOCIATIONS
  fi
  ((i=i+1))
done < "${1:-/dev/stdin}"
