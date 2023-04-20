from urllib import response
import boto3
import botocore
import jmespath
import xlsxwriter
import botocore.exceptions
import datetime
from datetime import timedelta, date
from dateutil import tz
import time
import logging
import logging.handlers
from google.oauth2.service_account import Credentials
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from oauth2client.client import HttpAccessTokenRefreshError
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import json
# API 토큰 파일 경로
TOKEN_PATH = "token.json"
# 클라이언트 시크릿 파일 경로
CLIENT_SECRET_FILE = "client_secret.json"

SLACK_BOT_TOKEN_FILE="slack_bot_token.json"
# API 권한 범위
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file"]


formatter = logging.Formatter('%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] - %(message)s')
fileHandler = logging.FileHandler('./resource_log.txt')
streamHandler =logging.StreamHandler()

fileHandler.setFormatter(formatter)
streamHandler.setFormatter(formatter)

fileHandler.setLevel(logging.ERROR)
streamHandler.setLevel(logging.INFO)

log = logging.getLogger()
log.addHandler(fileHandler)
log.addHandler(streamHandler)
log.setLevel(logging.INFO)

UNITS_MAPPING = [
    (1<<50, ' PB'),
    (1<<40, ' TB'),
    (1<<30, ' GB'),
    (1<<20, ' MB'),
    (1<<10, ' KB'),
    (1, (' byte', ' bytes')),
]
def pretty_size(bytes, units=UNITS_MAPPING):
    for factor, suffix in units:
        if bytes >= factor:
            break
    amount = int(bytes / factor)

    if isinstance(suffix, tuple):
        singular, multiple = suffix
        if amount == 1:
            suffix = singular
        else:
            suffix = multiple
    return str(amount) + suffix


def report_instance(ec2, cloudwatch, xlsx, title_format, colname_format, wrap_format, row_format, vulnerable_format, yellow_format):
    try:
        instance_list = ec2.describe_instances()
        output = jmespath.search("Reservations[*].Instances[*].[Tags[?Key=='Name'].Value, Tags[?Key=='cz-stage'].Value, Tags[?Key=='cz-project'].Value, Tags[?Key=='cz-owner'].Value, InstanceId, InstanceType, LaunchTime, Placement.AvailabilityZone, State.Name, PrivateIpAddress, PublicIpAddress, SecurityGroups[*].GroupName, SecurityGroups[*].GroupId, VpcId, SubnetId]", instance_list)

        result_sheet = xlsx.add_worksheet('EC2 instance')
        result_sheet.set_column('A:A', 40)
        result_sheet.set_column('B:B', 20)
        result_sheet.set_column('C:C', 15)
        result_sheet.set_column('D:D', 16)
        result_sheet.set_column('E:G', 13)
        result_sheet.set_column('H:H', 35)
        result_sheet.set_column('I:J', 25)
        result_sheet.set_column('K:K', 23)
        result_sheet.set_column('L:M', 15)
        result_sheet.set_column('N:N', 25)


        Columns = ["Name", "Instance ID", "Instance Type", "Availability Zone", "State", "Private IP", "Public IP", "Security Groups", "VPC ID", "Subnet ID", "cz-stage", "cz-project", "cz-owner", "Launch Time"]
    
        result_sheet.write(0, 0, "EC2 Instance List", title_format)

        col = 0 
        for ColName in Columns:
            result_sheet.write(1, col, ColName, colname_format)
            col += 1

        row = 2

        for instance in output:
            #instance = instance[0]
            #log.info(instance)
            instance_id = instance[0][1]
            # instance_attribute_list = ec2.describe_instance_attribute(Attribute='disableApiTermination', InstanceId=instance_id)
            # instance_disableapitermination_status = jmespath.search("DisableApiTermination.Value", instance_attribute_list)

            # status_alarm_list = cloudwatch.describe_alarms_for_metric(MetricName='StatusCheckFailed',Namespace='AWS/EC2',Dimensions=[{'Name': 'InstanceId','Value': instance_id},],)
            # status_alarm = jmespath.search("MetricAlarms[*].StateValue", status_alarm_list)

            # cpu_alarm_list = cloudwatch.describe_alarms_for_metric(MetricName='CPUUtilization',Namespace='AWS/EC2',Dimensions=[{'Name': 'InstanceId','Value': instance_id},],)
            # cpu_alarm = jmespath.search("MetricAlarms[*].StateValue", cpu_alarm_list)

            # if instance_disableapitermination_status == False:
            #     result_sheet.write(row, 10, instance_disableapitermination_status, vulnerable_format)
            # else:
            #     result_sheet.write(row, 10, instance_disableapitermination_status, row_format)

            # if status_alarm==[]:
            #     status_alarm= ['-']
            #     result_sheet.write(row, 11, status_alarm[0], vulnerable_format)
            # else:
            #     result_sheet.write(row, 11, status_alarm[0], row_format)

            # if cpu_alarm==[]:
            #     cpu_alarm= ['-']
            #     result_sheet.write(row, 12, cpu_alarm[0], vulnerable_format)
            # else:
            #     result_sheet.write(row, 12, cpu_alarm[0], row_format)


            for Name, Tag_cz_stage, Tag_cz_Project, Tag_cz_Owner, InstanceId, InstanceType, LaunchTime, AvailabilityZone, State, PrivateIpAddress, PublicIpAddress, SecurityGroupsName, SecurityGroupsId, VpcId, SubnetId in instance:
                LaunchTime = LaunchTime.strftime('%c')
                #log.info(instance)
                #log.info(Name)
                print(Name, Tag_cz_stage, Tag_cz_Project, Tag_cz_Owner)
                if Name==None:
                    Name=['-']

                #여기에 태그값을 넣을 수 있는 함수를 넣으면 되겠다.
                if Tag_cz_stage==[]:
                    Tag_cz_stage=['-']
                if Tag_cz_Project==[]:
                    Tag_cz_Project=['-']
                if Tag_cz_Owner==[]:
                    Tag_cz_Owner=['-']
                if State != 'terminated':
                    try:
                        Name[0]
                    except IndexError:
                        Name=['-']
                    result_sheet.write(row, 0, Name[0], row_format)
                    result_sheet.write(row, 1, InstanceId, row_format)
                    result_sheet.write(row, 2, InstanceType, row_format)
                    result_sheet.write(row, 3, AvailabilityZone, row_format)
                    result_sheet.write(row, 4, State, row_format if State == "running" else vulnerable_format)  
                    result_sheet.write(row, 5, PrivateIpAddress, row_format)
                    result_sheet.write(row, 6, PublicIpAddress, row_format)
                    result_sheet.write(row, 7, SecurityGroupsName[0]+" ("+SecurityGroupsId[0]+")", row_format)
                    result_sheet.write(row, 8, VpcId, row_format)
                    result_sheet.write(row, 9, SubnetId, row_format)
                    result_sheet.write(row, 10, Tag_cz_stage[0], row_format if Tag_cz_stage[0] != '-' else yellow_format)
                    result_sheet.write(row, 11, Tag_cz_Project[0], row_format if Tag_cz_Project[0] != '-' else yellow_format)
                    result_sheet.write(row, 12, Tag_cz_Owner[0], row_format if Tag_cz_Owner[0] != '-' else yellow_format)
                    result_sheet.write(row, 13, LaunchTime, row_format)
                    row += 1


        log.info("Instances ["+str(len(output))+"]")
    except botocore.exceptions.ClientError as e:
        log.error(e)
    log.info("=====Done=====")


def report_ebs(ec2, xlsx, title_format, colname_format, wrap_format, row_format, vulnerable_format):

    try:
        volume_list = ec2.describe_volumes()
        volume_names = jmespath.search("Volumes[*].VolumeId", volume_list)

        volume_info = []

        for name in volume_names:
            try:
                volume_name_info = ec2.describe_volumes(VolumeIds=[name])
                volume_output = jmespath.search("Volumes[*].[Tags[?Key=='Name'].Value, VolumeId, Attachments[*].State, State, Attachments[*].Device, AvailabilityZone, VolumeType, Size, Attachments[*].DeleteOnTermination, Encrypted, Attachments[*].InstanceId, CreateTime]", volume_name_info)

                volume_info.append(volume_output)
            except botocore.exceptions.ClientError as e:
                log.error(e)

        result_sheet = xlsx.add_worksheet('EBS')
        result_sheet.set_column('A:A', 45)
        result_sheet.set_column('B:B', 20)
        result_sheet.set_column('C:C', 18)
        result_sheet.set_column('D:D', 15)
        result_sheet.set_column('E:G', 13)
        result_sheet.set_column('H:H', 10)
        result_sheet.set_column('I:I', 12)
        result_sheet.set_column('J:J', 22)
        result_sheet.set_column('K:K', 20)
        result_sheet.set_column('L:L', 25)

        Columns = ["Volume Name", "Volume ID", "Attachment Status", "Volume Status", "Drive Path", "Availability Zone", "Volume Type", "Size", "Encryption", "Delete On Termination", "Attached Instance", "Create  Time"]
        result_sheet.write(0, 0, "EBS List", title_format)

        col = 0
        for ColName in Columns:
            result_sheet.write(1, col, ColName, colname_format)
            col += 1

        row = 2
        for Volume in volume_info:
            for Volume_Name, Volume_Id, Attachment_Status, Volume_Status, Drive_Path, AvailabilityZone, Volume_Type, Size, DeleteOnTermination, Encryption, Attached_Instance, Create_Time in Volume:
                Create_Time = Create_Time.strftime('%c')
                if Volume_Name==None or Volume_Name==[]:
                    Volume_Name = ['-']
                result_sheet.write(row, 0, Volume_Name[0], row_format)
                result_sheet.write(row, 1, Volume_Id, row_format)
                if Attachment_Status == []:
                    Attachment_Status = ["detached"]
                    result_sheet.write(row, 2, Attachment_Status[0], vulnerable_format)
                else:
                    result_sheet.write(row, 2, Attachment_Status[0], row_format)
                result_sheet.write(row, 3, Volume_Status, row_format)
                if Drive_Path == []:
                    Drive_Path = ['-']
                result_sheet.write(row, 4, Drive_Path[0], row_format)
                result_sheet.write(row, 5, AvailabilityZone, row_format)
                result_sheet.write(row, 6, Volume_Type, row_format)
                result_sheet.write(row, 7, str(Size) + " GB", row_format)
                if Encryption == False:
                    result_sheet.write(row, 8, Encryption, vulnerable_format)
                else:
                    result_sheet.write(row, 8, Encryption, row_format)
                if DeleteOnTermination == []:
                    DeleteOnTermination = ['-']
                result_sheet.write(row, 9, DeleteOnTermination[0], row_format)
                if Attached_Instance == []:
                    Attached_Instance = ['-']
                result_sheet.write(row, 10, Attached_Instance[0], row_format)
                result_sheet.write(row, 11, Create_Time, row_format)
                row += 1

        log.info("EBS ["+str(len(volume_info))+"]")
    except botocore.exceptions.ClientError as e:
        log.error(e)          
    log.info("=====Done=====")


def report_ami_snapshot(ec2, account_id, xlsx, title_format, colname_format, wrap_format, row_format, vulnerable_format):
    try:
        ami_list = ec2.describe_images(Owners=[account_id])
        ami_output = jmespath.search("Images[*].[Tags[?Key=='Name'].Value, Name, ImageId, Platform, PlatformDetails, CreationDate]", ami_list)

        result_sheet = xlsx.add_worksheet('AMI & Snapshot')
        result_sheet.set_column('A:A', 40)
        result_sheet.set_column('B:B', 70)
        result_sheet.set_column('C:C', 23)
        result_sheet.set_column('D:D', 30)
        result_sheet.set_column('E:E', 30)
        result_sheet.set_column('F:F', 30)

        Columns = ["Name Tag", "Name", "ID", "Platform", "Platform Detail", "Create Time"]
        result_sheet.write(0, 0, "AMI List", title_format)

        col = 0 
        for ColName in Columns:
            result_sheet.write(1, col, ColName, colname_format)
            col += 1

        row = 2
        for NameTag, Name, ID, Platform, Details, CreateTime in ami_output:
            if NameTag == None or NameTag == []:
                NameTag = ['-']
            result_sheet.write(row, 0, NameTag[0], row_format)
            result_sheet.write(row, 1, Name, row_format)
            result_sheet.write(row, 2, ID, row_format)
            result_sheet.write(row, 3, Platform, row_format)
            result_sheet.write(row, 4, Details, row_format)
            result_sheet.write(row, 5, CreateTime, row_format)
            row += 1

        log.info("-AMI ["+str(len(ami_output))+"]")

        row += 1


        snapshot_list = ec2.describe_snapshots(OwnerIds=[account_id])
        snapshot_output = jmespath.search("Snapshots[*].[Tags[?Key=='Name'].Value, SnapshotId, VolumeId, VolumeSize, StartTime]", snapshot_list)
        snapshot_next = jmespath.search("NextToken", snapshot_list)
        while snapshot_next != None:
            next_list = ec2.describe_snapshots(NextToken=snapshot_next,OwnerIds=[account_id])
            next_output = jmespath.search("Snapshots[*].[Tags[?Key=='Name'].Value, SnapshotId, VolumeId, VolumeSize, StartTime]", next_list)
            for Append in next_output:
                snapshot_output.append(Append)
            snapshot_next = jmespath.search("NextToken", snapshot_list)
        result_sheet.write(row, 0, "EBS Snapshot List", title_format)
        row += 1
        Columns = ["Name Tag", "Snapshot ID", "Volume ID", "Volume Size", "Create Time"]
        col = 0
        for ColName in Columns:
            result_sheet.write(row, col, ColName, colname_format)
            col += 1 
        row += 1
        for Name, SnapID, VolumeID, Size, CreateTime in snapshot_output:
            if Name == None or Name == []:
                Name = ['-']
            CreateTime = CreateTime.strftime('%c')
            result_sheet.write(row, 0, Name[0], row_format)
            result_sheet.write(row, 1, SnapID, row_format)
            result_sheet.write(row, 2, VolumeID, row_format) 
            result_sheet.write(row, 3, str(Size) + " GB", row_format) 
            result_sheet.write(row, 4, CreateTime, row_format) 
            row +=1
        log.info("EBS Snapshot ["+str(len(snapshot_output))+"]")

    except botocore.exceptions.ClientError as e:
        log.error(e)
    log.info("=====Done=====")

def send_slack_message(spreadsheet_url, slack_token, channel):
    client = WebClient(token=slack_token)

    try:
        response = client.chat_postMessage(
            channel=channel,
            text=f"새로운 스프레드 시트가 업로드되었습니다: {spreadsheet_url}"
        )
        print("Slack 메시지가 전송되었습니다.")
    except SlackApiError as e:
        print(f"Slack 메시지를 보내는 중 에러가 발생했습니다: {e}")




def get_credentials():
    creds = None

    # with open('new_credentials.json', 'r') as f:
    #     info = json.load(f)
    # credentials = Credentials.from_authorized_user_info(info)
    # print("확인")
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        print("확인 하기 위해 print")
        if creds and creds.expired and creds.refresh_token:
        # if creds.expired:
            try:
                creds.refresh(Request())
            except HttpAccessTokenRefreshError as e:
                print("토큰 갱신 실패:", e)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    return creds

def set_spreadsheet_public(file_id, drive_service):
    try:
        permission_body = {
            'type': 'anyone',
            'role': 'reader'
        }
        drive_service.permissions().create(fileId=file_id, body=permission_body).execute()
        print("스프레드 시트가 공개로 설정되었습니다.")
    except HttpError as error:
        print(f"An error occurred: {error}")


def upload_excel_to_google_sheets(excel_file):
    try:
        creds = get_credentials()
        drive_service = build("drive", "v3", credentials=creds)
        sheets_service = build("sheets", "v4", credentials=creds)

        file_metadata = {
            "name": os.path.basename(excel_file),
            "mimeType": "application/vnd.google-apps.spreadsheet",
        }
        media = MediaFileUpload(excel_file, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", resumable=True)

        file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
        print(f'File ID: "{file.get("id")}". 업로드 완료: {file.get("name")}.')

        spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{file.get('id')}"
        print(f"스프레드 시트 URL: {spreadsheet_url}")

        set_spreadsheet_public(file.get("id"), drive_service)

    except HttpError as error:
        print(f"An error occurred: {error}")
        file = None

    return file


def main():

    local_date = datetime.datetime.now()
    local_YMD = local_date.strftime('%Y-%m-%d')
    xlsx = xlsxwriter.Workbook(f'Resource-Report({local_YMD}).xlsx')
    excel_file=f"Resource-Report({local_YMD}).xlsx"
    title_format = xlsx.add_format({'bold':True, 'font_size':13, 'align':'center'})
    colname_format = xlsx.add_format({'bold':True, 'font_color':'white', 'bg_color':'#1E4E79', 'border':1})
    wrap_format = xlsx.add_format({'text_wrap': True, 'border':1})
    row_format = xlsx.add_format({'text_wrap':'true', 'font_size':10, 'align':'left', 'valign':'vcenter', 'border':1})
    vulnerable_format = xlsx.add_format({'text_wrap':'true', 'font_size':10, 'align':'left', 'valign':'vcenter', 'font_color':'red', 'bold':True, 'border':1})
    yellow_format = xlsx.add_format({'text_wrap':'true', 'font_size':10, 'align':'left', 'valign':'vcenter', 'bg_color':'yellow', 'bold':True, 'border':1})

    session = boto3.Session()
    
    #account_id = session.client("sts").get_caller_identity()["Account"]
    ec2 = session.client('ec2')
    cloudwatch = session.client('cloudwatch')
    # log.info("=====Create VPC Report=====")
    # report_vpc(ec2, xlsx, title_format, colname_format, wrap_format, row_format, vulnerable_format) #vpc #subnet 
    log.info("=====Create EC2 Instance Report=====")
    report_instance(ec2, cloudwatch, xlsx, title_format, colname_format, wrap_format, row_format, vulnerable_format,yellow_format) #instance


    xlsx.close()
     # Create a Aspose.Cells icense object
    uploaded_file=upload_excel_to_google_sheets(excel_file)

    if uploaded_file:
        with open(SLACK_BOT_TOKEN_FILE, "r") as file:
            data = json.load(file)
        SLACK_BOT_TOKEN=data['token']
        CHANNEL ="#superset-alert"
        spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{uploaded_file.get('id')}"
        send_slack_message(spreadsheet_url, SLACK_BOT_TOKEN, CHANNEL)


if __name__ == "__main__":
    main()
