import os
import google.auth
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# API 토큰 파일 경로
TOKEN_PATH = "token.json"
# 클라이언트 시크릿 파일 경로
CLIENT_SECRET_FILE = "client_secret.json"
# API 권한 범위
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file"]

def get_credentials():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    return creds

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

    except HttpError as error:
        print(f"An error occurred: {error}")
        file = None

    return file

if __name__ == "__main__":
    excel_file = "Resource-Report(2023-03-30).xlsx"  # 업로드할 엑셀 파일 이름
    upload_excel_to_google_sheets(excel_file)