# @Author: katie
# @Date:   2020-10-22T18:57:24-05:00
# @Last modified by:   katie
# @Last modified time: 2020-10-22T19:09:31-05:00



################################################################################
# Import Needed Packages                                                       #
################################################################################

import httplib2
import os

try:
    from apiclient import discovery
except:
    from googleapiclient import discovery

from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

################################################################################
# Authentication Class                                                         #
################################################################################

class googleDriveAuthenticate(object):
    """docstring for googleDriveAuthenticate."""

    def __init__(self, scopes = None, client_secret_file = None, application_name = None, authorization_file = None):
        self.scopes = scopes
        self.client_secret_file = client_secret_file
        self.application_name = application_name
        self.authorization_file = authorization_file

        self.credential_path = os.path.join(os.getcwd(),
                                           authorization_file)

        self.store = Storage(self.authorization_file)
        self.credentials = self.store.get()

    def googleDriveConnect(self):
        if not self.credentials or self.credentials.invalid:
            flow = client.flow_from_clientsecrets(self.client_secret_file, self.scopes)
            flow.user_agent = self.application_name
            if flags:
                credentials = tools.run_flow(flow, self.store, flags)
                print('Storing credentials to ' + self.credential_path)

        #Authorize credentials
        http = self.credentials.authorize(httplib2.Http())

        discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                            'version=v4')
        service = discovery.build('sheets', 'v4', http=http,
                                      discoveryServiceUrl=discoveryUrl)

        # Return the service
        return service
