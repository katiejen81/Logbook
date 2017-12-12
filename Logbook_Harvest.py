#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Google Logbook Harvester
Created on Wed May 31 21:41:35 2017
Written in Python2
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

from __future__ import division
import httplib2
import os

try:
    from apiclient import discovery
except:
    from googleapiclient import discovery

from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import csv

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


#Setting objects for credentials
scope = ('https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive.metadata.readonly')
client_secret = 'client_secret.json'
display_name = 'Logbook API Harvest'

#Setting the working directory
try:
    os.chdir('/media/katie/322f9f54-fb6e-4d56-b45c-9e2850394428/Katie Programs/Logbook')
except:
    os.chdir('/home/mike/Programs/Logbook')

working_dir = os.getcwd()

credential_dir = os.path.join(working_dir, '.credentials')

if not os.path.exists(credential_dir):
    os.makedirs(credential_dir)

credential_path = os.path.join(credential_dir,
                                   'logbook-google-sheets.json')

store = Storage(credential_path)
credentials = store.get()

if not credentials or credentials.invalid:
    flow = client.flow_from_clientsecrets(client_secret, scope)
    flow.user_agent = display_name
    if flags:
	credentials = tools.run_flow(flow, store, flags)


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

#Pull in the csv files that are downloaded and saved to the computer
files = os.listdir('/home/mike/Documents/Logbook/XJT_Schedules')

schedules = list()
for i in files:
    if '7048196' not in i:
        continue
    schedules.append('/home/mike/Documents/Logbook/XJT_Schedules' + '/' + i)

#Bring the csv file to dictionary
schedule_dict = list()
for i in schedules:
    with open(i, 'r') as infile:
	reader = csv.DictReader(infile)
	for row in reader:
	    schedule_dict.append(row)

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

#Testing the sequencer
#for i in schedule_dict:
#    print(i['Date'] + '\t' + i['Origin'] + '\t' + i['Dest'] + '\t' + str(i['Sequence']))

#Sequence trips - Logbook
dates = list()
for i in value_dict:
    if i['DATE'] in dates:
        continue
    dates.append(i['DATE'])

for i in dates:
    seq_list = list()
    for j in value_dict:
	if j['DATE'] == i:
		if (j['FROM'], j['TO']) not in seq_list:
		    seq_list.append((j['FROM'], j['TO']))
		    j['Sequence'] = 1
		    counter = 1
		elif (j['FROM'], j['TO']) in seq_list:
		    counter = counter + 1
		    j['Sequence'] = counter

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
