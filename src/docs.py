# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# Changed

from collections import defaultdict
from typing import Dict

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

DISCOVERY_DOC = "https://docs.googleapis.com/$discovery/rest?version=v1"
SCOPES = ["https://www.googleapis.com/auth/documents.readonly"]

class Docs:
    def __init__(self):
        self.credentials = self.get_credentials()
        self.docs_service = build("docs", "v1", http=self.credentials.authorize(Http()), discoveryServiceUrl=DISCOVERY_DOC)

    def get_credentials(self):
        """
        Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth 2.0 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        store = file.Storage("token_docs.json")
        credentials = store.get()

        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets("credentials.json", SCOPES)
            credentials = tools.run_flow(flow, store)

        return credentials

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
    doc_content = docs.read_details('1eZy4PhMN22iiVA4Kcf5W7GZoyrL4umBxtoMQpWB6LCU')
    print(doc_content)
