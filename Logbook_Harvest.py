# @Author: katie
# @Date:   2018-04-15T13:59:02-05:00
# @Last modified by:   katie
# @Last modified time: 2020-01-25T16:01:40-06:00



#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Google Logbook Harvester
Created on Wed May 31 21:41:35 2017
Written in Python3
Copyright (C) 2017  Kathryn Tanner

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

#Import our packages
import httplib2
import os
import csv
from datetime import datetime

try:
    from apiclient import discovery
except:
    from googleapiclient import discovery

from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

#Setting objects for credentials
scope = ('https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive.metadata.readonly')
client_secret = 'client_secret.json'
display_name = 'Logbook API Harvest'

# Going to set up in the shell script the location for the program

#Getting credentials
credential_path = os.path.join(os.getcwd(),
                                   'authorization.json')
store = Storage('authorization.json')
credentials = store.get()

if not credentials or credentials.invalid:
    flow = client.flow_from_clientsecrets(client_secret, scope)
    flow.user_agent = display_name
    credentials = tools.run_flow(flow, store)
    print('Storing credentials to ' + credential_path)

#Authorize credentials
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

# Ask the user where the files that contain the company information are located
file_path = input('Please enter the full path where the downloaded schedule files are located\n ' + \
'hit enter to look for files in /home/mike/Downloads: ')

# Create a default file location
if file_path == '':
    file_path = '/home/mike/Downloads'

#Pull in all files, need to loop through several pages
files_list = os.listdir(file_path)

schedules = list()
for i in files_list:
    if '7048196' not in i:
        continue
    schedules.append(file_path + '/' + i)

schedule_data = list()
for i in schedules:
    with open(i, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            schedule_data.append(row)

# Get the schedule_headers - if exists
if len(schedule_data) == 0:
    pass
else:
    schedule_headers = schedule_data[0]

#Pull in the schedule
temp_dict = list()
for i in schedule_data:
    if i == schedule_headers:
        continue
    data = dict()
    for j, k in zip(i, schedule_headers):
        data[k] = j
    temp_dict.append(data)

#Create a hashkey that allows us to identify unique values
for i in temp_dict:
    i['Hashkey'] = hash(frozenset(i.items()))

#Dedupe our list
seen_before = list()
schedule_dict = list()
for i in temp_dict:
    if i['Hashkey'] in seen_before:
        continue
    seen_before.append(i['Hashkey'])
    schedule_dict.append(i)

#Sequence trips
def sequencer(data, datefield, Originvar, Destvar):
    dates = list()
    for i in data:
        if i[datefield] in dates:
            continue
        dates.append(i[datefield])
    for i in dates:
        pair_count = dict()
        for j in data:
            if j[datefield] != i:
                continue
            pair = (j[Originvar], j[Destvar])
            if pair_count.get(pair, '') == '':
                pair_count[pair] = 1
                j['Sequence'] = 1
            else:
                pair_count[pair] += 1
                j['Sequence'] = pair_count[pair]
    return data

to_add = sequencer(to_add, 'DATE', 'FROM', 'TO')

schedule_dict = sequencer(schedule_dict, 'Date', 'Origin', 'Dest')

#Normalize dates so that they can be joined
for i in to_add:
    if i['DATE'] == '':
        continue
    i['d'] = datetime.strptime(i['DATE'], '%m/%d/%Y')

for i in schedule_dict:
    i['d'] = datetime.strptime(i['Date'], '%m/%d/%Y')

#Join the Information in the logbook to the schedule

Total_sheet = list()

for i in to_add:
    for j in schedule_dict:
        dr_date = '/'.join(('0' if len(x)<2 else '')+x for x in i['DATE'].split('/'))
        if j['Origin'] == i['FROM'] \
        and j['Dest'] == i['TO'] \
        and j['Date'] == dr_date \
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
                if ['CROSS COUNTRY'] == 0:
                    data['CROSS COUNTRY'] = 0
                else:
                    data['CROSS COUNTRY'] = j['Block']
                data['REMARKS AND ENDORSEMENTS'] = i.get('REMARKS AND ENDORSEMENTS', '')
                data['Timestamp'] = i['Timestamp']
                data['TOTAL DURATION OF FLIGHT'] = j['Block']
                data['AIRPLANE MULTI-ENGINE LAND'] = j['Block']
                if (['PILOT IN COMMAND'] == 0) | (['PILOT IN COMMAND'] == None):
                    data['PILOT IN COMMAND'] = 0
                    data['SECOND IN COMMAND'] = j['Block']
                else:
                    data['SECOND IN COMMAND'] = 0
                    data['PILOT IN COMMAND'] = j['Block']
                Total_sheet.append(data)

#Append to the master and join to the master
for i in Total_sheet:
    del i['d']
    value_dict_master.append(i)

#Look for values that were not appended
Timestamps = list()
for i in value_dict_master:
    Timestamps.append(i['Timestamp'])

Missing = list()
for i in value_dict:
    if i['Timestamp'] not in Timestamps:
        Missing.append(i)

#Now we need to return the delta to a list of lists so that we can append
delta = list()
for i in Total_sheet:
    row = list()
    for j in headers_master:
        row.append(i[j])
    delta.append(row)

#Append to the test spreadsheet
body = {
        'values': delta
        }

resultTest = service.spreadsheets().values().append(
        spreadsheetId = spreadsheetId, range=rangeName,
        valueInputOption='USER_ENTERED', body=body).execute()

#Return the missing list to a list of lists
Missing_sheet = list()

Missing_sheet.append(headers)
for i in Missing:
    row = list()
    for j in headers:
        row.append(i.get(j, ''))
    Missing_sheet.append(row)

rangeMiss = 'Missing'
body = {
        'values': Missing_sheet
        }

resultMissing = service.spreadsheets().values().update(
        spreadsheetId = spreadsheetId, range=rangeMiss,
        valueInputOption='USER_ENTERED', body=body).execute()
