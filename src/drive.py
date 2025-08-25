import io
from googleapiclient.http import MediaIoBaseDownload
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import logging

class Drive:
    def __init__(self):
        '''
        Creates the `drive_service`, linking to Google Drive
        '''
        self.drive_service = build('drive', 'v3', credentials=self.get_credentials())

    def get_credentials(self) -> dict:
        """
        Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth 2.0 flow is completed to obtain the new credentials.

        Returns:
            Credentials: Credentials, the obtained credential.
        """

        # If modifying these scopes, delete the file token_drive.json.
        SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

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

    def get_ep_details_id(self, folder: dict) -> dict:
        """
        Gets `ep#_details` file id and name dictionary 

        Args:
            folder (dict): name and id of episode folder

        Returns:
            the id of the details file in the specified folder
        """
        results = self.drive_service.files().list(
            pageSize=5, fields="nextPageToken, files(id, name)",q=f"name = '{folder['name']}_details' and '{folder['id']}' in parents and trashed=false").execute()
        items = results.get('files', [])

        if not items:
            print(f'No {folder["name"]} folder in root.')
            return

        ep_details = items[0]
        return ep_details

    def get_ep_folder_id(self, ep_num: str) -> dict:
        """
        Gets `ep#_folder` folder id and name

        Args:
            ep_num (str): name of episode folder

        Returns:
            dict: id and name of ep#_folder.

        """

        try:
            results = self.drive_service.files().list(
                pageSize=5, fields="nextPageToken, files(id, name)",q=f"name = '{ep_num}' and mimeType = 'application/vnd.google-apps.folder' and trashed=false").execute()
            ep_folders = results.get('files', [])

            if not ep_folders:
                print(f'No ep# folder in root.')
                return
            
            ep_folder = ep_folders[0]
            return ep_folder
                
        except HttpError as error:
            print(f'An error occurred: {error}')
    
    def download_mp3(self, folder: dict) -> dict:
        """
        Downloads the `ep#.mp3` file under `ep_folder/raw/`

        Args:
            folder (dict): name and id of episode folder

        Returns:
            the id of the {ep_num} folder, if found
        """
        results = self.drive_service.files().list(
                pageSize=5, fields="nextPageToken, files(id, name)",q=f"'{folder['id']}' in parents and name='raw' and mimeType = 'application/vnd.google-apps.folder' and trashed=false").execute()
        raw = results.get('files', [])

        if not raw:
            print(f"No raw folder in {self.folder['name']}.")
            return

        results = self.drive_service.files().list(
                pageSize=5, fields="nextPageToken, files(id, name)",q=f"'{raw[0]['id']}' in parents and name='{folder['name']}.mp3' and mimeType != 'application/vnd.google-apps.folder' and trashed=false").execute()
        mp3s = results.get('files', [])

        if not mp3s:
            print(f"No {folder['name']}.mp3 in {raw[0]['name']}")
            return
        
        mp3 = mp3s[0]
        
        try:
            file_id = mp3['id']

            request = self.drive_service.files().get_media(fileId=file_id)
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request)

            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print(f'Download {int(status.progress() * 100)}%')

        except HttpError as error:
            print(f'An error occurred: {error}')
            file = None

        with open(f'{mp3['name']}','wb') as f:
            f.write(file.getbuffer())
        
        return mp3

if __name__ == '__main__':
    drive = Drive()
    folder = drive.get_ep_folder_id('ep248')
    print(f'{folder=}')
    details = drive.get_ep_details_id(folder)
    print(f'{details=}')
    mp3 = drive.download_mp3(folder)
    print(f'{mp3=}')

