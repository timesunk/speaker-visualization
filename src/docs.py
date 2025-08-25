from collections import defaultdict
from typing import Dict

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/documents.readonly"]

class Docs:
    def __init__(self):
        self.docs_service  = build("docs", "v1", credentials=self.get_credentials())

    def get_credentials(self):
        """
        Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth 2.0 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        creds = None
        if os.path.exists("token_docs.json"):
            creds = Credentials.from_authorized_user_file("token_docs.json", SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open("token_docs.json", "w") as token:
                token.write(creds.to_json())

        return creds

        # try:
        #     service = build("docs", "v1", credentials=creds)

    def get_doc(self,id):
        """
        Returns the document with the specified id
        """
        return self.docs_service.documents().get(documentId=id).execute()

    def read_details(self, id: str) -> Dict[str , list[str]]:
        """
        Reads ep#_details document and returns dictionary of relevant values
        """
        doc = self.get_doc(id)

        elements = doc["body"]["content"]
        d = defaultdict(list)
        for value in elements:
            if "table" in value:
                for row in value["table"]["tableRows"]:

                    left_col, right_col = row["tableCells"]
                    k = left_col['content'][0]['paragraph']['elements'][0]['textRun']['content'].strip()

                    if k == 'Categories': continue

                    elif k == 'Title':
                        d[k].append(right_col['content'][0]['paragraph']['elements'][0]['textRun']['content'].strip())

                    elif k == 'Shownotes':
                        for c in right_col['content']:
                            base = c['paragraph']['elements'][0]['textRun']
                            text, url = base['content'].strip(), base['textStyle'].get('link',{}).get('url','') # safer
                            d[k].append({'text':text, 'url':url})
                    else:
                        for c in right_col['content']:
                            d[k].append(c['paragraph']['elements'][0]['textRun']['content'].strip())
        return d

if __name__ == "__main__":
    docs = Docs()
    doc_content = docs.read_details('1IYtVUONoDgRq5dDqDcSFknMyQEmy3kZRbwqDnw9vItU')
    print(doc_content)
