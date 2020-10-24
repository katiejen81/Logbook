# @Author: katie
# @Date:   2017-07-09T19:41:52-05:00
# @Last modified by:   katie
# @Last modified time: 2020-10-22T21:34:41-05:00



#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Create the Logbook Pages
Created on Sun Jun 11 14:27:07 2017
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
from datetime import datetime
import pandas as pd

from core.Drive_Data_Fetch import googleSpreadsheetFetch
from core.Page_Write_Functions import pageWriteFunctions

# Get data from drive
gDrive_init = googleSpreadsheetFetch(
    scopes = 'https://www.googleapis.com/auth/spreadsheets.readonly',
    client_secret_file = 'client_secret.json',
    application_name = 'Logbook API Print',
    authorization_file = 'authorization.json',
    spreadsheetId = '15FeoThcHzYceUEoIR6uegF4HFH-jJKzW6paitZ9dipM',
    rangeName = 'XJT_Logbook_CLEAN!B:AE',
    dictConvert = True
)

# Define Default Values from the Google Spreadsheet
na_replace = {
    'AIRCRAFT IDENT':'N/A',
    'FROM':'N/A',
    'TO':'N/A',
    'FROM':'N/A',
    'TOTAL DURATION OF FLIGHT':0.0,
    'AIRPLANE SINGLE-ENGINE LAND':0.0,
    'AIRPLANE SINGLE-ENGINE SEA':0.0,
    'AIRPLANE MULTI-ENGINE LAND':0.0,
    'LANDINGS DAY':0,
    'LANDINGS NIGHT':0,
    'NIGHT':0.0,
    'ACTUAL INSTRUMENT':0.0,
    'SIMULATED INSTRUMENT (HOOD)':0.0,
    'FLIGHT SIMULATOR':0.0,
    'CROSS COUNTRY':0.0,
    'SOLO':0.0,
    'PILOT IN COMMAND':0.0,
    'SECOND IN COMMAND':0.0,
    'DUAL RECEIVED':0.0,
    'AS FLIGHT INSTRUCTOR':0.0,
    'REMARKS AND ENDORSEMENTS':'No Remarks'
}

gSheetData = gDrive_init.getGoogleSpreadsheetData(default_values=na_replace)

format_maps = {
    'TOTAL DURATION OF FLIGHT':'{:,.1f}',
    'AIRPLANE SINGLE-ENGINE LAND':'{:,.1f}',
    'AIRPLANE SINGLE-ENGINE SEA':'{:,.1f}',
    'AIRPLANE MULTI-ENGINE LAND':'{:,.1f}',
    'LANDINGS DAY':'{:,.0f}',
    'LANDINGS NIGHT':'{:,.0f}',
    'NIGHT':'{:,.1f}',
    'ACTUAL INSTRUMENT':'{:,.1f}',
    'SIMULATED INSTRUMENT (HOOD)':'{:,.1f}',
    'FLIGHT SIMULATOR':'{:,.1f}',
    'CROSS COUNTRY':'{:,.1f}',
    'SOLO':'{:,.1f}',
    'PILOT IN COMMAND':'{:,.1f}',
    'SECOND IN COMMAND':'{:,.1f}',
    'DUAL RECEIVED':'{:,.1f}',
    'AS FLIGHT INSTRUCTOR':'{:,.1f}'
}

data = pd.DataFrame(gSheetData)




for key, value in format_maps.items():
    data[key] = pd.to_numeric(data[key], downcast="float")
    # data[key] = data[key].apply(value.format)

# Initialize page write functions
pw_init = pageWriteFunctions()

page1_list = ['DATE', 'AIRCRAFT MAKE AND MODEL', 'AIRCRAFT IDENT',
              'FROM', 'TO', 'TOTAL DURATION OF FLIGHT', 'AIRPLANE SINGLE-ENGINE LAND',
              'AIRPLANE SINGLE-ENGINE SEA', 'AIRPLANE MULTI-ENGINE LAND',
              'LANDINGS DAY', 'LANDINGS NIGHT']

page2_list = ['NIGHT', 'ACTUAL INSTRUMENT', 'SIMULATED INSTRUMENT (HOOD)', 'FLIGHT SIMULATOR',
              'CROSS COUNTRY', 'SOLO', 'PILOT IN COMMAND', 'SECOND IN COMMAND',
              'DUAL RECEIVED', 'AS FLIGHT INSTRUCTOR', 'REMARKS AND ENDORSEMENTS']

index_list = pw_init.page_chunk(gSheetData, page1_list=page1_list, page2_list=page2_list)

def get_combined_totals(prev_totals, current_totals):
    combined_totals = {}


def get_totals(start, end, data, columns, prev_totals):
    cut_data = data.iloc[start:end]

    column_totals = {}
    combined_totals = {}
    for i in columns:
        if i not in ['DATE', 'AIRCRAFT MAKE AND MODEL', 'AIRCRAFT IDENT',
                     'FROM', 'TO', 'APPROACH', 'REMARKS AND ENDORSEMENTS']:
            if i in ['LANDINGS DAY', 'LANDINGS NIGHT']:
                column_totals[i] = round(cut_data[i].sum(), 0)
                combined_totals[i] = int(round(prev_totals.get(i, 0) + column_totals[i], 0))
            else:
                column_totals[i] = round(cut_data[i].sum(), 1)
                combined_totals[i] = round(prev_totals.get(i, 0) + column_totals[i], 1)
        else:
            column_totals[i] = ''
            combined_totals[i] = ''

    return combined_totals




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
            writer.write(l)
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
            writer.write('<th class="p1box" colspan="2" rowspan = "4">Totals</th>')
            writer.write('</tr>')
        writer.write('<tr>')
        writer.write('<td class="boldcenter" colspan="3">' + n + ' </td>')
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
            writer.write(l)
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
                writer.write('<th class="p2box" rowspan="4" align="center" style="font-size: 9px;">I certify that the entries in this ' + \
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
              'LANDINGS DAY', 'LANDINGS NIGHT']

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

year = year_compute(index_list[0], page1_dict)
prev = page1_write(index_list[0], page1_dict, page1_list, prev1_totals)

##Writing the html file
with open('Logbook_Print.html', 'w') as writer:
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
