#!/bin/bash

## Date Set
year=`date +%Y`
month=`date +%m`
day=`date +%d`
hour=`date +%H`



# aws ec2 describe-instances --query 'Reservations[].Instances[].InstanceId' --region ap-northeast-2 > instance-id.txt
# total_instance_number=`cat instance-id.txt | wc -l | xargs`
# total_instance_number=$((total_instance_number-2))
# pwd
# ls
# str_instance_id=""
# for ((idx=2; idx<=$total_instance_number+1; idx++)); do
#     instance_id=`cat instance-id.txt | head -$idx | tail -1 | xargs`
#     instance_id=${instance_id:0:19}
#     str_instance_id="$str_instance_id $instance_id"
# done
# aws ec2 describe-instances --instance-ids $str_instance_id --region ap-northeast-2 > result.json
# aws s3 cp result.json s3://${{ secrets.s3_bucket }}/ec2/$year/$month/$day/$hour/result.json