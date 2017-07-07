#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Create the Logbook Pages
Created on Sun Jun 11 14:27:07 2017
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

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

import numpy as np
from datetime import datetime

#Setting objects for credentials
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Logbook API Print'

#Setting the working directory
try:
    os.chdir('/home/katie/Documents/Logbook')
#working directory on desktop computer
except:
    os.chdir('/media/katie/322f9f54-fb6e-4d56-b45c-9e2850394428/Katie Programs/Logbook')

#Getting credentials
credential_path = os.path.join(os.getcwd(),
                                   'authorization.json')
store = Storage('authorization.json')
credentials = store.get()

if not credentials or credentials.invalid:
    flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
    flow.user_agent = APPLICATION_NAME
    if flags:
        credentials = tools.run_flow(flow, store, flags)
        print('Storing credentials to ' + credential_path)

#Authorize credentials
http = credentials.authorize(httplib2.Http())

discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

#Pull in data from the master spreadsheet
spreadsheetId = '15FeoThcHzYceUEoIR6uegF4HFH-jJKzW6paitZ9dipM'
rangeName = 'XJT_Logbook_CLEAN!B:AE'
result = service.spreadsheets().values().get(
    spreadsheetId=spreadsheetId, range=rangeName).execute()
values_master = result.get('values', [])

headers_master = values_master[0]

#Filter for only what I need and convert to dictionary
values_list = headers_master[0:17]

value_dict_master = list()

for i in range(1, len(values_master)):
    j = values_master[i]
    data = dict()
    for l, m in zip(values_list, j):
        data[l] = m
    value_dict_master.append(data)

#Defining the functions that print the table

##Defining the header row and the fixed widths of the columns - page even
def p1header_row(values, year):
    writer.write('<table class=page1>')
    writer.write('<col width="70">')
    writer.write('<col width="80">')
    writer.write('<col width="80">')
    writer.write('<col width="60">')
    writer.write('<col width="60">')
    writer.write('<col width="85">')
    writer.write('<col width="95">')
    writer.write('<col width="85">')
    writer.write('<col width="95">')
    writer.write('<col width="85">')
    writer.write('<col width="65">')
    writer.write('<col width="40">')
    writer.write('<col width="40">')
    writer.write('<tr>')
    writer.write('<th colspan = "3">YEAR ' \
                 + year \
                 + '</th>')
    writer.write('<th colspan = "2">ROUTE OF FLIGHT</th>')
    writer.write('<th rowspan = "2">TOTAL DURATION OF FLIGHT</th>')
    writer.write('<th colspan = "5">AIRCRAFT CATEGORY AND CLASS</th>')
    writer.write('<th colspan = "2">LANDINGS</th>')
    writer.write('</tr><tr>')
    for i in values:
        if i == 'TOTAL DURATION OF FLIGHT':
            continue
        elif 'LANDINGS' in i:
            i = i.split(' ')[1]
        j = '<td class=secondrow>' + i + '</td>'
        writer.write(j)
    writer.write('</tr>')

##Defining the header row and fixed widths of the columns - page odd
def p2header_row(values):
    writer.write('<table class=page2>')
    writer.write('<col width="60">')
    writer.write('<col width="70">')
    writer.write('<col width="70">')
    writer.write('<col width="70">')
    writer.write('<col width="65">')
    writer.write('<col width="50">')
    writer.write('<col width="75">')
    writer.write('<col width="75">')
    writer.write('<col width="75">')
    writer.write('<col width="75">')
    writer.write('<col width="255">')
    writer.write('<tr>')
    writer.write('<th colspan = "3">CONDITIONS OF FLIGHT</th>')
    writer.write('<th rowspan = "2">FLIGHT SIMULATOR</th>')
    writer.write('<th colspan = "6">TYPE OF PILOTING TIME</th>')
    writer.write('<th rowspan = "2">REMARKS AND ENDORSEMENTS</th>')
    writer.write('</tr><tr>')
    for i in values:
        if i == 'FLIGHT SIMULATOR':
            continue
        elif i == 'REMARKS AND ENDORSEMENTS':
            continue
        j = '<td class=secondrow>' + i + '</td>'
        writer.write(j)
    writer.write('</tr>')

##Function that develops the page1 and page2 dictionaries
def page_divide(header_list, input_dict):
    output_dict = list()
    for i in input_dict:
        dict1 = dict()
        for key, value in i.iteritems():
            if key in header_list:
                dict1[key] = value
            else:
                continue
        output_dict.append(dict1)
    return output_dict

##Function that dynamically defines the pages - page 2
def page_chunk(input_dict):
    length_list = [60, 70, 70, 70, 65, 50, 75, 75, 75, 75, 245]
    record_rows = 0
    temp_list = list()
    temp_height_list = list()
    height_list = list()
    value_list = list()
    row_num = 0
    for i in input_dict:
        index = row_num
        temp_list.append(index)
        col_rows = list()
        for j, k in zip(page2_list, length_list):
            length = len(i.get(j, ''))
            length_px = length * 7
            if np.ceil(length_px/k) == 0:
                rows = 1
            else:
                rows = int(np.ceil(length_px/k))
            col_rows.append(rows)
        record_rows = record_rows + max(col_rows)
        temp_height_list.append(max(col_rows) * 17)
        row_num = row_num + 1
        if record_rows > 37:
            start = temp_list[len(temp_list) - 1]
            del temp_height_list[len(temp_height_list) - 1]
            del temp_height_list[len(temp_height_list) - 1]
            del temp_list[len(temp_list) - 1]
            value_list.append(temp_list)
            height_list.append(temp_height_list)
            temp_list = [start]
            record_rows = max(col_rows)
            temp_height_list = [record_rows * 17]
        else:
            continue
    value_list.append(temp_list)
    height_list.append(temp_height_list)
    last = height_list[len(height_list) - 1]
    del height_list[len(height_list) - 1]
    for m in height_list:
        line = True
        while line == True:
            if sum(m) == 612:
                line = False
            elif sum(m) < 612:
                for n in range(len(m)):
                    m[n] = m[n] + 1
                    if sum(m) == 612:
                        line = False
                    else:
                        continue
    height_list.append(last)
    index_list = list()
    for i, j in zip(value_list, height_list):
        val = (min(i), max(i), j)
        index_list.append(val)
    return index_list

##Function that writes out the year for the header of the table
def year_compute(input_range, input_dict):
    start = input_range[0]
    end = input_range[1]
    table = input_dict[start:end]
    temp_list = list()
    for j in table:
        date = datetime.strptime(j['DATE'], '%M/%d/%Y').date().strftime('%Y')
        if date in temp_list:
            continue
        temp_list.append(date)
    if len(temp_list) == 1:
        year = temp_list[0]
    else:
        year = '/'.join(temp_list)
    return year

##Function to write out the table rows and cells past the header row - Page 1
def page1_write(input_range, input_data, input_headers, prev_totals):
    start = input_range[0]
    end = input_range[1]
    row_height_list = input_range[2]
    print_list = input_data[start:end]
    curr_totals = dict()
    combined_totals = dict()
    for i, j in zip(print_list, row_height_list):
        writer.write('<tr>')
        for k in input_headers:
            l = '<td style="height:' + str(j) + 'px;">' + i.get(k, ' ') + '</td>'
            writer.write(l.encode('utf-8'))
            if k not in ['DATE', 'AIRCRAFT MAKE AND MODEL', 'AIRCRAFT IDENT',
                         'FROM', 'TO', 'APPROACH', 'REMARKS AND ENDORSEMENTS']:
                try:
                    total = float(i.get(k, 0))
                except:
                    total = 0
                if k in ['LANDINGS DAY', 'LANDINGS NIGHT']:
                    curr_totals[k] = int(curr_totals.get(k, 0) + total)
                    combined_totals[k] = int(prev_totals.get(k, 0) + curr_totals.get(k, 0))
                else:
                    curr_totals[k] = round(curr_totals.get(k, 0) + total, 1)
                    combined_totals[k] = round(prev_totals.get(k, 0) + curr_totals.get(k, 0), 1)
            else:
                curr_totals[k] = ''
                combined_totals[k] = ''
                continue
        writer.write('</tr>')
    for m, n in zip([curr_totals, prev_totals, combined_totals],
                    ['TOTALS THIS PAGE', 'AMT. FORWARDED', 'TOTALS TO DATE']):
        if n == 'TOTALS THIS PAGE':
            writer.write('<tr>')
            writer.write('<th colspan="2" rowspan = "4">Totals</th>')
        writer.write('<tr>')
        writer.write('<th colspan="3">' + n + ' </th>')
        for k in input_headers:
            if k in ['DATE', 'AIRCRAFT MAKE AND MODEL', 'AIRCRAFT IDENT', 'FROM',
                     'TO']:
                continue
            else:
                writer.write('<td>' + str(m.get(k, 0)) + '</td>')
        writer.write('</tr>')
    writer.write('</table>')
    return combined_totals

def page2_write(input_range, input_data, input_headers, prev_totals):
    start = input_range[0]
    end = input_range[1]
    row_height_list = input_range[2]
    print_list = input_data[start:end]
    curr_totals = dict()
    combined_totals = dict()
    for i, j in zip(print_list, row_height_list):
        writer.write('<tr>')
        for k in input_headers:
            l = '<td style="height:' + str(j) + 'px;">' + i.get(k, ' ') + '</td>'
            writer.write(l.encode('utf-8'))
            if k not in ['DATE', 'AIRCRAFT MAKE AND MODEL', 'AIRCRAFT IDENT',
                         'FROM', 'TO', 'APPROACH', 'REMARKS AND ENDORSEMENTS']:
                try:
                    total = float(i.get(k, 0))
                except:
                    total = 0
                else:
                    curr_totals[k] = round(curr_totals.get(k, 0) + total, 1)
                    combined_totals[k] = round(prev_totals.get(k, 0) + curr_totals.get(k, 0), 1)
            else:
                curr_totals[k] = ''
                combined_totals[k] = ''
                continue
        writer.write('</tr>')
    for m, n in zip([curr_totals, prev_totals, combined_totals],
                    ['TOTALS THIS PAGE', 'AMT. FORWARDED', 'TOTALS TO DATE']):
        writer.write('<tr>')
        for l in page2_list:
            if l == 'REMARKS AND ENDORSEMENTS' and n == 'TOTALS THIS PAGE':
                writer.write('<th rowspan="4" align="center" style="font-size: 9px;">I certify that the entries in this ' + \
                             'log are true<br><br>____________________________________' + \
                             '<br>PILOT SIGNATURE</th>')
            elif l == 'REMARKS AND ENDORSEMENTS' and n != 'TOTALS THIS PAGE':
                continue
            else:
                writer.write('<td>' + str(m.get(l, 0)) + '</td>')
        writer.write('</tr>')
    writer.write('</table>')
    return combined_totals

#Preparing the data for write to the html table
##Dividing the dictionaries to pages
page1_list = ['DATE', 'AIRCRAFT MAKE AND MODEL', 'AIRCRAFT IDENT',
              'FROM', 'TO', 'TOTAL DURATION OF FLIGHT', 'AIRPLANE SINGLE-ENGINE LAND',
              'AIRPLANE SINGLE-ENGINE SEA', 'AIRPLANE MULTI-ENGINE LAND',
              'ROTORCRAFT HELICOPTER', 'GLIDER', 'LANDINGS DAY', 'LANDINGS NIGHT']

page2_list = ['NIGHT', 'ACTUAL INSTRUMENT', 'SIMULATED INSTRUMENT (HOOD)', 'FLIGHT SIMULATOR',
              'CROSS COUNTRY', 'SOLO', 'PILOT IN COMMAND', 'SECOND IN COMMAND',
              'DUAL RECEIVED', 'AS FLIGHT INSTRUCTOR', 'REMARKS AND ENDORSEMENTS']


page1_dict = page_divide(page1_list, value_dict_master)
page2_dict = page_divide(page2_list, value_dict_master)

##Chunking the pages and defining the records for breaks
index_list = page_chunk(page2_dict)


#Using the functions to write out to an html table
##Starting dictionary
prev1_totals = dict()
prev2_totals = dict()
##Writing the html file
with open('Logbook_Print.html', 'wb') as writer:
    writer.write('<html>')
    writer.write('<head>')
    writer.write('<link rel="stylesheet" href="style.css">')
    writer.write('</head>')
    writer.write('<title>Mike Tanner Logbook</title>')
    writer.write('<body>')
    writer.write('<h1>Placeholder for Cover Page</h1>')
    writer.write('<p>Michael Tanner</p>')
    writer.write('<p>Logbook from insert_date to insert_date</p>')
    writer.write('<div class="pagebreak"> </div>')
    for i in index_list:
        year = year_compute(i, page1_dict)
        p1header_row(page1_list, year)
        prev = page1_write(i, page1_dict, page1_list, prev1_totals)
        prev1_totals = prev
        p2header_row(page2_list)
        prev = page2_write(i, page2_dict, page2_list, prev2_totals)
        prev2_totals = prev
    writer.write('</body>')
    writer.write('</html>')
writer.close()
