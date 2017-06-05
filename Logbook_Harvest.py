#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Google Logbook Harvester
Created on Wed May 31 21:41:35 2017
Written in Python2
@author: katie
"""

#Import our packages
from __future__ import print_function
from __future__ import division
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import numpy as np

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None
    
#Setting objects for credentials
SCOPES = ('https://www.googleapis.com/auth/spreadsheets.readonly',
          'https://www.googleapis.com/auth/drive.metadata.readonly')
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Logbook API Harvest'

#Setting the working directory
os.chdir('/home/katie/Documents/Logbook')

#Getting credentials
store = Storage('/home/katie/Documents/Logbook/authorization.json')
credential_path = os.path.join(os.getcwd(),
                                   'sheets.googleapis.com-Logbook.json')

flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
flow.user_agent = APPLICATION_NAME
if flags:
    credentials = tools.run_flow(flow, store, flags)

credentials = store.get()
print('Storing credentials to ' + credential_path)

#Pull in data
http = credentials.authorize(httplib2.Http())

discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

spreadsheetId = '1LNX6rDPsm8iN47LjPdK_8BJmhSvL4SqdGe79I9mvFaY'
rangeName = 'Form Responses 1!A:P'
result = service.spreadsheets().values().get(
    spreadsheetId=spreadsheetId, range=rangeName).execute()
values = result.get('values', [])

#I think that I want a dictionary structure
headers = values[0]

value_dict = list()

for i in range(1, len(values)):
    j = values[i]
    data = dict()
    for l, m in zip(headers, j):
        data[l] = m
    value_dict.append(data)
    
#Pull in a list of file so that we can find the schedule
drive = discovery.build('drive', 'v3', http=http)

files = drive.files().list().execute()

files = files.get('files', [])

for i in files:
    if i['name'] != '7048196_201705':
        continue
    fileid = i['id']

#Pull in the schedule    
rangeName2 = '7048196_201705!A:N'
result2 = service.spreadsheets().values().get(
        spreadsheetId=fileid, range=rangeName2).execute()
schedule = result2.get('values', [])


headers_sched = schedule[0]

schedule_dict = list()

for i in range(1, len(schedule)):
    j = schedule[i]
    data = dict()
    for l, m in zip(headers_sched, j):
        data[l] = m
    schedule_dict.append(data)
    
#Join the Information in the logbook to the schedule

Total_sheet = list()

for i in value_dict:
    for j in schedule_dict:
        if j['Origin'] == i['FROM'] \
            and j['Dest'] == i['TO'] \
            and j['Date'] == i['DATE']:
                data = j
                data['AIRCRAFT MAKE AND MODEL'] = i['AIRCRAFT MAKE AND MODEL']
                data['LANDINGS DAY'] = i['LANDINGS DAY']
                data['LANDINGS NIGHT'] = i['LANDINGS NIGHT']
                data['NIGHT'] = i['NIGHT']
                data['ACTUAL INSTRUMENT'] = i['ACTUAL INSTRUMENT']
                data['APPROACH'] = i['APPROACH']
                data['FLIGHT SIMULATOR'] = i['FLIGHT SIMULATOR']
                data['CROSS COUNTRY'] = i['CROSS COUNTRY']
                data['REMARKS AND ENDORSEMENTS'] = i.get('REMARKS AND ENDORSEMENTS', '')
                data['Timestamp'] = i['Timestamp']
                data['TOTAL DURATION OF FLIGHT'] = j['Block']
                data['AIRPLANE MULTI-ENGINE LAND'] = j['Block']
                data['PILOT IN COMMAND'] = 0
                data['SECOND IN COMMAND'] = j['Block']    
                Total_sheet.append(data)

