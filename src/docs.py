from collections import defaultdict
from typing import Dict
from pprint import pprint

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError

class Docs:
    def __init__(self):
        '''
        Creates the `docs_service`, to read all Google Docs
        '''
        self.docs_service  = build("docs", "v1", credentials=self.get_credentials())

    def get_credentials(self) -> dict:
        """
        Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth 2.0 flow is completed to obtain the new credentials.

        Returns:
            Credentials: Credentials, the obtained credential.
        """

        # If modifying these scopes, delete the file token_drive.json.
        SCOPES = ["https://www.googleapis.com/auth/documents.readonly"]

        creds = None
        if os.path.exists("token_docs.json"):
            creds = Credentials.from_authorized_user_file("token_docs.json", SCOPES)

        try:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
        except RefreshError:
            print("Refresh token invalid, regenerating...")
            creds = None

        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

            with open("token_docs.json", "w") as token:
                token.write(creds.to_json())

        return creds

    def get_doc(self, id: str) -> dict:
        """
        Gets the full document with the specified id

        Args:
            id (str): id of document

        Returns:
            doc: full document

        """
        try:
            doc = self.docs_service.documents().get(documentId=id).execute()

        except HttpError as err:
            print(err)

        return doc

    def read_details(self, id: str) -> Dict[str , list[str]]:
        """
        Reads ep#_details document and returns dictionary of relevant values

        Args:
            id (str): id of document

        Returns:
            d: dictionary of all the details from the table in ep#_details.docx file
        """
        doc = self.get_doc(id)


        elements = doc["body"]["content"]
        pprint(elements)
        d = defaultdict(list)
        for value in elements:
            if "table" in value:
                for row in value["table"]["tableRows"]:

                    left_col, right_col = row["tableCells"]
                    k = left_col['content'][0]['paragraph']['elements'][0]['textRun']['content'].strip()

                    if k == 'Categories': continue # ignore

                    # only take the first title
                    elif k == 'Title':
                        d[k].append(right_col['content'][0]['paragraph']['elements'][0]['textRun']['content'].strip())

                    # process each link, to add a dictionary with text and url
                    elif k == 'Shownotes':
                        for c in right_col['content']:
                            base = c['paragraph']['elements'][0]['textRun']
                            text, url = base['content'].strip(), base['textStyle'].get('link',{}).get('url','') # safer
                            d[k].append({'text':text, 'url':url})

                    # the rest of the rows are simple key : value
                    else:
                        for c in right_col['content']:
                            d[k].append(c['paragraph']['elements'][0]['textRun']['content'].strip())
        return d

if __name__ == "__main__":
    docs = Docs()
    doc_content = docs.read_details('1xH6Q6OccbMn5N8SuXtyxlDWrl_uO3AQ9-74DA0-5l2w')
    pprint(doc_content)
