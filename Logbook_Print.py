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
    writer.write('<table>')
    writer.write('<col width="70">')
    writer.write('<col width="80">')
    writer.write('<col width="80">')
    writer.write('<col width="50">')
    writer.write('<col width="50">')
    writer.write('<col width="85">')
    writer.write('<col width="95">')
    writer.write('<col width="85">')
    writer.write('<col width="95">')
    writer.write('<col width="85">')
    writer.write('<col width="85">')
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
        j = '<td class=secondrow>' + i + '</td>'
        writer.write(j)
    writer.write('</tr>')
    
##Defining the header row and fixed widths of the columns - page odd
def p2header_row(values):
    writer.write('<table>')
    writer.write('<col width="70">')
    writer.write('<col width="70">')
    writer.write('<col width="70">')
    writer.write('<col width="80">')
    writer.write('<col width="75">')
    writer.write('<col width="75">')
    writer.write('<col width="75">')
    writer.write('<col width="75">')
    writer.write('<col width="75">')
    writer.write('<col width="75">')
    writer.write('<col width="385">')
    writer.write('<tr>')
    writer.write('<th colspan = "3">CONDITIONS OF FLIGHT</th>')
    writer.write('<th rowspan = "2">FLIGHT SIMULATOR</th>')
    writer.write('<th colspan = "6">TYPE OF PILOTING TIME</th>')
    writer.write('<th rowspan = "2">REMARKS AND ENDORSEMENTS</th>')
    writer.write('</tr><tr>')
    for i in values:
        if i == 'FLIGHT SIMULATOR':
            continue
        j = '<td class=secondrow>' + i + '</td>'
        writer.write(j)
    writer.write('</tr>')


##Function that dynamically defines the pages - page 1
def p2page_chunk(input_dict):
    length_list = [70, 70, 70, 80, 75, 75, 75, 75, 75, 75, 385]
    record_rows = 0
    temp_list = list()
    value_list = list()
    for i in input_dict:
        index = input_dict.index(i)
        temp_list.append(index)
        col_rows = list()
        for j, k in zip(values_list, length_list):
            length = len(i.get(j, ''))
            length_px = length * 6
            if np.ceil(length_px/k) == 0:
                rows = 1
            else:
                rows = int(np.ceil(length_px/k))
            col_rows.append(rows)
        record_rows = record_rows + max(col_rows)
        if record_rows > 39:
            start = temp_list[len(temp_list) - 1]
            del temp_list[len(temp_list) - 1]
            value_list.append(temp_list)
            temp_list = [start]
            record_rows = max(col_rows)
        else:
            continue
    value_list.append(temp_list)

    index_list = list()
    for i in value_list:
        val = (min(i), max(i))
        index_list.append(val)
    return index_list

index_list = page_chunk(value_dict_master)

##Function to write out the table rows and cells past the header row
def page_write(input_range, input_data, input_headers, prev_totals):
    start = input_range[0]
    end = input_range[1]
    print_list = input_data[start:end]
    curr_totals = dict()
    combined_totals = dict()
    for i in print_list:
        writer.write('<tr>')
        for j in input_headers:
            k = '<td>' + i.get(j, ' ') + '</td>'
            writer.write(k.encode('utf-8'))
            if j not in ['DATE', 'AIRCRAFT MAKE AND MODEL', 'AIRCRAFT IDENT',
                         'FROM', 'TO', 'APPROACH', 'REMARKS AND ENDORSEMENTS']:
                try:
                    total = float(i.get(j, 0))
                except:
                    total = 0
                if j in ['LANDINGS DAY', 'LANDINGS NIGHT']:
                    curr_totals[j] = int(curr_totals.get(j, 0) + total)
                    combined_totals[j] = int(prev_totals.get(j, 0) + curr_totals.get(j, 0))
                else:
                    curr_totals[j] = round(curr_totals.get(j, 0) + total, 1)
                    combined_totals[j] = round(prev_totals.get(j, 0) + curr_totals.get(j, 0), 1)
            else:
                curr_totals[j] = ''
                combined_totals[j] = ''
                continue
        writer.write('</tr>')
    for m, n in zip([prev_totals, curr_totals, combined_totals],
                    ['Previous', 'Current', 'Combined']):
        if n == 'Previous':
            writer.write('<tr>')
            writer.write('<th colspan="2" rowspan = "4">Totals</th>')
        writer.write('<tr>')
        writer.write('<th colspan="3">' + n + ' Page Totals</th>')
        writer.write('<td>' + str(m.get('TOTAL DURATION OF FLIGHT', 0)) + '</td>')
        writer.write('<td>' + str(m.get('AIRPLANE MULTI-ENGINE LAND', 0)) + '</td>')
        writer.write('<td>' + str(m.get('LANDINGS DAY', 0)) + '</td>')
        writer.write('<td>' + str(m.get('LANDINGS NIGHT', 0)) + '</td>')
        writer.write('<td>' + str(m.get('NIGHT', 0)) + '</td>')
        writer.write('<td>' + str(m.get('ACTUAL INSTRUMENT', 0)) + '</td>')
        writer.write('<td>' + str(m.get('APPROACH', 0)) + '</td>')
        writer.write('<td>' + str(m.get('CROSS COUNTRY', 0)) + '</td>')
        writer.write('<td>' + str(m.get('FLIGHT SIMULATOR', 0)) + '</td>')
        writer.write('<td>' + str(m.get('PILOT IN COMMAND', 0)) + '</td>')
        writer.write('<td>' + str(m.get('SECOND IN COMMAND', 0)) + '</td>')
        writer.write('<td>' + str(m.get('REMARKS AND ENDORSEMENTS', 0)) + '</td>')
        writer.write('</tr>')
    writer.write('<td colspan = "6" rowspan = "2">I certify that the entries and totals are true as of </td>')
    writer.write('<td colspan = "3" rowspan = "2">Date: </td>')
    writer.write('<td colspan = "8" rowspan = "2">Signed: </td>')
    writer.write('</table>')
    return combined_totals

#Using the functions to write out to an html table
##Starting dictionary
prev_totals = dict()

##Writing the html file
with open('Logbook_Print.html', 'wb') as writer:
    writer.write('<html>')
    writer.write('<head>')
    writer.write('<link rel="stylesheet" href="style.css">')
    writer.write('</head>')
    writer.write('<title>Mike Tanner Logbook</title>')
    writer.write('<body>')
    for i in index_list:
        header_row(values_list)
        prev = page_write(i, value_dict_master, values_list, prev_totals)
        prev_totals = prev
    writer.write('</body>')
    writer.write('</html>')
writer.close()
