# @Author: katie
# @Date:   2020-10-22T19:20:45-05:00
# @Last modified by:   katie
# @Last modified time: 2020-10-22T21:30:28-05:00



from core.Drive_Authenticate import googleDriveAuthenticate

class googleSpreadsheetFetch(googleDriveAuthenticate):
    """docstring for googleSpreadsheetFetch."""

    def __init__(self, scopes = None,
                client_secret_file = None,
                application_name = None,
                authorization_file = None,
                spreadsheetId = None,
                rangeName = None,
                colNoStart = 0,
                colNoEnd = 21,
                dictConvert = True):
        super(googleSpreadsheetFetch, self).__init__(
            scopes = scopes,
            client_secret_file = client_secret_file,
            application_name = application_name,
            authorization_file = authorization_file
        )
        self.spreadsheetId = spreadsheetId
        self.rangeName = rangeName
        self.dictConvert = dictConvert
        self.colNoStart = colNoStart
        self.colNoEnd = colNoEnd

        self.gDriveAccess = self.googleDriveConnect()

    def getGoogleSpreadsheetData(self, default_values={}):
        result = self.gDriveAccess.spreadsheets().values().get(
            spreadsheetId=self.spreadsheetId, range=self.rangeName).execute()

        values_master = result.get('values', [])
        headers_master = values_master[0]

        values_list = headers_master[self.colNoStart:self.colNoEnd]

        if not self.dictConvert:
            return values_list
        else:
            value_dict_master = list()
            for i in range(1, len(values_master)):
                j = values_master[i]
                data = dict()
                for l, m in zip(values_list, j):
                    data[l] = m
                value_dict_master.append(data)

            # Clean up and place a default value if it does not exist
            for i in value_dict_master:
                for repl_val in default_values.items():
                    i[repl_val[0]] = i.get(repl_val[0], repl_val[1])
                    if i[repl_val[0]] == '':
                        i[repl_val[0]] = repl_val[1]
                    elif i[repl_val[0]] == None:
                        i[repl_val[0]] = repl_val[1]
                    elif i[repl_val[0]] == '\n':
                        i[repl_val[0]] = repl_val[1]
                    else:
                        i[repl_val[0]] = i[repl_val[0]]

            return value_dict_master
