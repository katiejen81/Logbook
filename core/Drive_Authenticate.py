# @Author: katie
# @Date:   2020-10-22T18:57:24-05:00
# @Last modified by:   katie
# @Last modified time: 2020-10-24T09:13:53-05:00



################################################################################
# Import Needed Packages                                                       #
################################################################################

import pickle
import os
from googleapiclient import discovery
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

################################################################################
# Authentication Class                                                         #
################################################################################

class googleDriveAuthenticate(object):
    """
    Author  :   Google, katie
    Purpose :   To complete the OAuth chain to access the spreadsheet data
    Inputs  :   scopes (required) - the area of the API we want to access
            :   client_secret_file (required) - where the client secrets are stored
            :   authorization_file (required) - where the access token is stored
    Outputs :   authorized connection to google drive scoped area
    Notes   :   code obtained and slightly modified from
            :   https://developers.google.com/sheets/api/quickstart/python
    """

    def __init__(self, scopes = None, client_secret_file = None, application_name = None, authorization_file = None):
        self.scopes = scopes
        self.client_secret_file = client_secret_file
        self.authorization_file = authorization_file

        self.credential_path = os.path.join(os.getcwd(),
                                           self.authorization_file)


    def googleDriveConnect(self):
        creds = None
        if os.path.exists(self.credential_path):
            with open(self.credential_path, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.client_secret_file,
                    scopes
                )
                creds = flow.run_local_server(port=0)
                with open(self.credential_path, 'wb') as token:
                    pickle.dump(creds, token)

        service = discovery.build('sheets', 'v4', credentials=creds)

        # Return the service
        return service
