import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token_drive.json.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

class Drive:
    def __init__(self):
        self.credentials = self.get_credentials()
        self.drive_service = build('drive', 'v3', credentials=self.credentials)

    def get_credentials(self):
        """
        Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth 2.0 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """

        creds = None
        if os.path.exists('token_drive.json'):
            creds = Credentials.from_authorized_user_file('token_drive.json', SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open('token_drive.json', "w") as token:
                token.write(creds.to_json())

        return creds

    def find_details_id(self, folder: dict) -> str:
        """
        Returns the id of the details file in the specified folder
        """
        results = self.drive_service.files().list(
            pageSize=5, fields="nextPageToken, files(id, name)",q=f"'{folder['id']}' in parents and trashed=false").execute()
        items = results.get('files', [])

        if not items:
            print(f'No ep{folder["name"]} folder in root.')
            return

        for item in items:
            if item['name'].endswith('details'):
                return item['id']

    def find_details(self, ep_num:str) -> str:
        """
        Returns the id of the {ep_num} details file if found
        """

        try:
            results = self.drive_service.files().list(
                pageSize=50, fields="nextPageToken, files(id, name)",q="'root' in parents and name contains 'ep' and mimeType = 'application/vnd.google-apps.folder' and trashed=false").execute()
            ep_folders = results.get('files', [])

            if not ep_folders:
                print(f'No ep# folder in root.')
                return
            
            for folder in ep_folders:
                if folder['name'][2:] == ep_num:
                    self.folder = folder
                    return self.find_details_id(folder), ep_num
            print(f'No ep{ep_num} found in root.')

        except HttpError as error:
            print(f'An error occurred: {error}')
    
    def download_mp3(self) -> str:
        results = self.drive_service.files().list(
                pageSize=50, fields="nextPageToken, files(id, name)",q=f"'{self.folder['id']}' in parents and name='raw' and mimeType = 'application/vnd.google-apps.folder' and trashed=false").execute()
        raw = results.get('files', [])
        print(raw)

        if not raw:
            print(f"No raw folder in {self.folder['name']}.")
            return

        results = self.drive_service.files().list(
                pageSize=50, fields="nextPageToken, files(id, name)",q=f"'{raw[0]['id']}' in parents and name='{self.folder['name']}.mp3' and mimeType != 'application/vnd.google-apps.folder' and trashed=false").execute()
        mp3 = results.get('files', [])
        print(mp3)

        if not mp3:
            print(f"No {self.folder['name']}.mp3 in {raw[0]['name']}")
            return
        
        print(mp3)

        try:
            file_id = mp3[0]['id']

            request = self.drive_service.files().get_media(fileId=file_id)
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print(f'Download {int(status.progress() * 100)}.')

        except HttpError as error:
            print(f'An error occurred: {error}')
            file = None

        with open(f'{self.folder["name"]}.mp3','wb') as f:
            f.write(file.getbuffer())
        
        return f'{self.folder["name"]}.mp3'

    def simple_test(self) -> str: 
        try:
            results = (
                self.drive_service.files()
                .list(pageSize=10, fields="nextPageToken, files(id, name)")
                .execute()
            )
            items = results.get("files", [])

            if not items:
                print("No files found.")
                return
            
            print("Files:")
            for item in items:
                print(f"{item['name']} ({item['id']})")

        except HttpError as error:
            print(f'An error occurred: {error}')

if __name__ == '__main__':
    drive = Drive()
    drive.simple_test()
    # id = drive.find_details('246')
    # print(id)
    # drive.download_mp3()
