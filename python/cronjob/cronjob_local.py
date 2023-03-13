import boto3
import botocore
import argparse
import botocore.exceptions
import datetime
from datetime import timedelta, date
from dateutil import tz
import logging
import logging.handlers
import json

formatter = logging.Formatter('%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] - %(message)s')
streamHandler =logging.StreamHandler()

streamHandler.setFormatter(formatter)

streamHandler.setLevel(logging.INFO)

log = logging.getLogger()
log.addHandler(streamHandler)
log.setLevel(logging.INFO)

def ec2_instance(ec2, cloudwatch):
    try:
        instance_list = ec2.describe_instances()
        with open('result.json', 'w') as f:
            for i in range(len(instance_list['Reservations'])):
                # TypeError: Object of type datetime is not JSON serializable -> del LaunchTime
                del instance_list['Reservations'][i]['Instances'][0]["LaunchTime"]
                del instance_list['Reservations'][i]['Instances'][0]["BlockDeviceMappings"]
                del instance_list['Reservations'][i]['Instances'][0]["NetworkInterfaces"]
                del instance_list['Reservations'][i]['Instances'][0]["UsageOperationUpdateTime"]
                f.write(json.dumps(instance_list['Reservations'][i]['Instances'][0])+ '\n')
    except botocore.exceptions.ClientError as e:
        log.error(e)

def main(region_args, profile_args):
    local_date = datetime.datetime.now()
    local_YMD = local_date.strftime('%Y/%m/%d')
    session = boto3.Session(region_name=region_args, profile_name=profile_args)
    
    #account_id = session.client("sts").get_caller_identity()["Account"]
    ec2 = session.client('ec2')
    cloudwatch = session.client('cloudwatch')
    dynamodb= session.resource('dynamodb')
    table=dynamodb.Table('secret-value')
    response = table.scan()
    items =response['Items']
    for i in range(len(items)):
        ec2 = boto3.Session(
            aws_access_key_id=items[i]['access_key'],
            aws_secret_access_key=items[i]['secret_key'],
            region_name='ap-northeast-2'
        ).client('ec2')
        ec2_instance(ec2, cloudwatch) #instance
        file_path=items[i]['account']+'/ec2/'+local_YMD+'/result.json'
        s3_client=session.client('s3')
        with open("result.json", "rb") as f:
            s3_client.upload_fileobj(f, items[i]['service'], file_path)
 

def get_arguments():
    # local_date = datetime.datetime.now()
    # local_YMD = local_date.strftime('%Y-%m-%d')
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', required=False, default='default', help='Account Credential Name')
    parser.add_argument('-r', required=False, default='ap-northeast-2', help='Region')
    args = parser.parse_args()
    return args.r, args.p


if __name__ == "__main__":
    region_args, profile_args= get_arguments()
    main(region_args, profile_args)
