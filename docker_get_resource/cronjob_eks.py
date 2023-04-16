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

def ec2_instance(ec2):
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

def sts_role():
    #sts = session.client('sts')
    sts = boto3.client('sts')
    response = sts.assume_role(
    RoleArn='arn:aws:iam::595367679687:role/AssumableRole_750876142122',
    RoleSessionName='AssumeRoleSession'
    )
    ec2 = boto3.client('ec2',
        aws_access_key_id=response['Credentials']['AccessKeyId'],
        aws_secret_access_key=response['Credentials']['SecretAccessKey'],
        aws_session_token=response['Credentials']['SessionToken']
    )
    return ec2
    # Use the temporary credentials to access the S3 bucket
    
#def main(region_args, profile_args):
def main():
    local_date = datetime.datetime.now()
    local_YMD = local_date.strftime('%Y/%m/%d')
    #session = boto3.Session(region_name=region_args, profile_name=profile_args)
    ec2=sts_role()

    #account_id = session.client("sts").get_caller_identity()["Account"]
    # ec2 = boto3.client('ec2')
    # cloudwatch = boto3.client('cloudwatch')
    # dynamodb= boto3.resource('dynamodb')
    # table=dynamodb.Table('secret-value')
    # response = table.scan()
    # items =response['Items']
    # for i in range(len(items)):
    #     ec2 = boto3.Session(
    #         aws_access_key_id=items[i]['access_key'],
    #         aws_secret_access_key=items[i]['secret_key'],
    #         region_name='ap-northeast-2'
    #     ).client('ec2')
    ec2_instance(ec2) #instance
    file_path='8888888888/ec2/'+local_YMD+'/result.json'
    s3_client=boto3.client('s3')
    with open("result.json", "rb") as f:
        s3_client.upload_fileobj(f, 'mad-master-bucket', file_path)
 

def get_arguments():
    # local_date = datetime.datetime.now()
    # local_YMD = local_date.strftime('%Y-%m-%d')
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', required=False, default='default', help='Account Credential Name')
    parser.add_argument('-r', required=False, default='ap-northeast-2', help='Region')
    args = parser.parse_args()
    return args.r, args.p


if __name__ == "__main__":
    #region_args, profile_args= get_arguments()
    #main(region_args, profile_args)
    main()