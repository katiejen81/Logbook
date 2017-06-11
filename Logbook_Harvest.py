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
SCOPES = ('https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive.metadata.readonly')
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Logbook API Harvest'

#Setting the working directory
os.chdir('/home/katie/Documents/Logbook')
#working directory on desktop computer
os.chdir('/media/katie/322f9f54-fb6e-4d56-b45c-9e2850394428/Katie Programs/Logbook')

#Getting credentials
store = Storage('authorization.json')
credential_path = os.path.join(os.getcwd(),
                                   'sheets.googleapis.com-Logbook.json')

flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
flow.user_agent = APPLICATION_NAME
if flags:
    credentials = tools.run_flow(flow, store, flags)

credentials = store.get()
print('Storing credentials to ' + credential_path)

#Pull in data from the current spreadsheet
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
    
#Now let's pull in the master file
spreadsheetId = '15FeoThcHzYceUEoIR6uegF4HFH-jJKzW6paitZ9dipM'
rangeName = 'XJT_Logbook_CLEAN!A:AE'
result = service.spreadsheets().values().get(
    spreadsheetId=spreadsheetId, range=rangeName).execute()
values_master = result.get('values', [])

headers_master = values_master[0]

value_dict_master = list()

for i in range(1, len(values_master)):
    j = values_master[i]
    data = dict()
    for l, m in zip(headers_master, j):
        data[l] = m
    value_dict_master.append(data)
    
#Find the entries that are not in the master file
existing = list()
for i in value_dict_master:
    existing.append(i.get('Timestamp', ''))
    
to_add = list()
for i in value_dict:
    if i['Timestamp'] in existing:
        continue
    to_add.append(i)
    
#Pull in a list of file so that we can find the schedule
drive = discovery.build('drive', 'v3', http=http)

files = drive.files().list().execute()

#Pull in all files, need to loop through several pages
files_list = list()
while True:
    if files.get('nextPageToken', None) == None:
        break
    for i in files['files']:
        files_list.append(i)
    nextPage = dict()
    nextPage['pageToken'] = files['nextPageToken']
    files = drive.files().list(**nextPage).execute()
    
schedules = list()
for i in files_list:
    if '7048196' not in i['name']:
        continue
    fileid = (i['id'], i['name'])
    schedules.append(fileid)

#Pull in the schedule
for i in schedules:
    rangeName2 =  i[1] + '!A:N'
    result2 = service.spreadsheets().values().get(
        spreadsheetId=i[0], range=rangeName2).execute()
    if schedules.index(i) == 0:
        schedule = (result2.get('values', []))
    else:
        schedule.append((result2.get('values', [])))

schedule_headers = schedule[0]
schedule_dict = list()        
for i in range(1, len(schedule)):
    j = schedule[i]
    data = dict()
    for l, m in zip(schedule_headers, j):
        data[l] = m
    schedule_dict.append(data)

#Sequence trips - Schedule
dates = list()
for i in schedule_dict:
    if i['Date'] in dates:
        continue
    dates.append(i['Date'])
   
for i in dates:
    seq_list = list()
    for j in schedule_dict:
        if j['Date'] == i:
            if (j['Origin'], j['Dest']) not in seq_list:
                seq_list.append((j['Origin'], j['Dest']))
                j['Sequence'] = 1
                counter = 1 
            elif (j['Origin'], j['Dest']) in seq_list:
                counter = counter + 1
                j['Sequence'] = counter
                 
#Sequence trips - Logbook
dates = list()
for i in value_dict:
    if i['DATE'] in dates:
        continue
    dates.append(i['DATE'])

for i in dates:
    seq_list = list()
    for j in value_dict:
        if (j['FROM'], j['TO']) not in seq_list:
            seq_list.append((j['FROM'], j['TO']))
            j['Sequence'] = 1
            counter = 1 
        elif (j['FROM'], j['TO']) in seq_list:
            counter = counter + 1
            j['Sequence'] = counter            
    
#Join the Information in the logbook to the schedule

Total_sheet = list()

for i in value_dict:
    for j in schedule_dict:
        if j['Origin'] == i['FROM'] \
            and j['Dest'] == i['TO'] \
            and j['Date'] == i['DATE'] \
            and j['Sequence'] == i['Sequence']:
                data = j
                data['AIRCRAFT MAKE AND MODEL'] = i['AIRCRAFT MAKE AND MODEL']
                data['AIRCRAFT IDENT'] = i['AIRCRAFT IDENT']
                data['LANDINGS DAY'] = i['LANDINGS DAY']
                data['DATE'] = i['DATE']
                data['FROM'] = i['FROM']
                data['TO'] = i['TO']
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
                
#Append to the master
for i in Total_sheet:
    value_dict_master.append(i)
    
#Look for values that were not appended
Timestamps = list()
for i in value_dict_master:
    Timestamps.append(i['Timestamp'])
    
Missing = list()
for i in value_dict:
    if i['Timestamp'] not in Timestamps:
        Missing.append(i)
        
#Things left to do
#Figure out how to append the new data to the old
#Figure out how to create a new sheet with the missing data

#Now we need to return the delta to a list of lists so that we can append
delta = list()
for i in Total_sheet:
    row = list()
    for j in headers_master:
        row.append(i[j])
    delta.append(row)