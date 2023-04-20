import gspread
from oauth2client.service_account import ServiceAccountCredentials
import boto3
import os
from google.oauth2.service_account import Credentials
from google.oauth2.credentials import Credentials
from oauth2client.client import HttpAccessTokenRefreshError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from gspread_formatting import *
from gspread_formatting import get_effective_format

# AWS 리소스에 대한 클라이언트를 생성합니다.
# 스프레드 시트 인증 정보를 로드합니다.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file"]
TOKEN_PATH = "token.json"
# 클라이언트 시크릿 파일 경로
CLIENT_SECRET_FILE = "client_secret.json"


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

def main():
    creds=get_credentials()
    client = gspread.authorize(creds)
    sheet = client.open('Resource-Report(2023-04-20)').sheet1
    # yellow_cells = sheet.range('A1:N5') # 노란색 셀의 범위를 가져옵니다.
    # start_row = 1  # 시작 행
    # end_row =   5# 끝 행
    # start_col = 1  # 시작 열
    # end_col = 14  # 끝 열
    ec2_client = boto3.client('ec2', region_name='ap-northeast-2')

    table_data = sheet.get_all_values()
    for row in table_data:
        for num in range(10,13):
            resource_id=row[1]
            try:
                response = ec2_client.create_tags(
                Resources=[resource_id],
                Tags=[{'Key': table_data[1][num], 'Value': row[num]}]
                )
            except:
                print("오류")
            
            

    # for row in table_data:
    #     row_values = row[start_col-1:end_col]  # 시작 열과 끝 열 사이의 데이터만 추출
    #     for cell_value in row_values:
    #         cell = sheet.find(cell_value)  # 셀 값이 일치하는 셀 찾기
            
    
    #         cell_row = cell.row  # 셀의 행 번호 가져오기
    #         cell_col = cell.col 
    #         cell_value = sheet.cell(cell_row, cell_col).value
    #         print(cell_value)
    #         cell_format = get_effective_format(sheet, cell)  # 셀의 서식 정보 가져오기
            # cell_bg_color = cell_format.backgroundColor  # 셀의 배경색 정보 가져오기
            # print("셀 값: ", cell_value)
            # print("셀 배경색: ", cell_bg_color)
    # # AWS 리소스에 대한 클라이언트를 생성합니다.
    # ec2_client = boto3.client('ec2', region_name='ap-northeast-2')

    # for cell in yellow_cells:
        
    #     tag_key = sheet.cell(1, cell.col).value
    #     print(tag_key)
    #     # tag_value = cell.value
    #     # resource_id = sheet.cell(cell.row, 1).value
        
    #     # response = ec2_client.create_tags(
    #     #     Resources=[resource_id],
    #     #     Tags=[{'Key': "create_id", 'Value': "value_id"}]
    #     # )

    #     # print(f"태그를 추가했습니다. 리소스 ID: {resource_id}, 키: {tag_key}, 값: {tag_value}")



if __name__ == "__main__":

    main()
