import io
import shutil

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

from oauth2client import file, client, tools


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
        store = file.Storage('token_drive.json')
        credentials = store.get()

        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
            credentials = tools.run_flow(flow, store)
        return credentials

    def find_details_id(self,folder: dict) -> str:
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
        ep_num defaults to 'latest'
        """

        try:
            results = self.drive_service.files().list(
                pageSize=50, fields="nextPageToken, files(id, name)",q="'root' in parents and name contains 'ep' and mimeType = 'application/vnd.google-apps.folder' and trashed=false").execute()
            ep_folders = results.get('files', [])

            if not ep_folders:
                print(f'No ep# folder in root.')
                return
            
            if ep_num == 'latest':
                latest_ep_folder = sorted(ep_folders, key=lambda a: int(a['name'][2:]), reverse=True)[0]
                self.folder = latest_ep_folder
                return self.find_details_id(latest_ep_folder), latest_ep_folder['name'][2:]

            else:
                for folder in ep_folders:
                    if folder['name'][2:] == ep_num:
                        self.folder = folder
                        return self.find_details_id(folder), ep_num
                print(f'No ep{ep_num} found in root.')

        except HttpError as error:
            print(f'An error occurred: {error}')
    
    def download_mp3(self):
        results = self.drive_service.files().list(
                pageSize=50, fields="nextPageToken, files(id, name)",q=f"'{self.folder['id']}' in parents and name='raw' and mimeType = 'application/vnd.google-apps.folder' and trashed=false").execute()
        raw = results.get('files', [])

        if not raw:
            print(f"No raw folder in {self.folder['name']}.")
            return

        results = self.drive_service.files().list(
                pageSize=50, fields="nextPageToken, files(id, name)",q=f"'{raw[0]['id']}' in parents and name='{self.folder['name']}.mp3' and mimeType != 'application/vnd.google-apps.folder' and trashed=false").execute()
        mp3 = results.get('files', [])

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

if __name__ == '__main__':
    drive = Drive()
    id = drive.find_details('latest')
    drive.download_mp3()