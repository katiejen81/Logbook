# @Author: katie
# @Date:   2017-07-09T19:41:52-05:00
# @Last modified by:   katie
# @Last modified time: 2020-10-24T11:50:28-05:00



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

import pandas as pd

from core.Drive_Data_Fetch import googleSpreadsheetFetch
from core.Page_Write_Functions import pageWriteFunctions

# Get data from drive
gDrive_init = googleSpreadsheetFetch(
    scopes = 'https://www.googleapis.com/auth/spreadsheets.readonly',
    client_secret_file = 'client_secret.json',
    authorization_file = 'token.pickle',
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
data_formatted = pd.DataFrame(gSheetData)
for key, value in format_maps.items():
    data[key] = pd.to_numeric(data[key], downcast="float")
    data_formatted[key] = pd.to_numeric(data_formatted[key], downcast="float")
    data_formatted[key] = data_formatted[key].apply(value.format)

data_dict = data_formatted.to_dict(orient='records)

import numpy as np
def page_chunk(input_dict, page1_list=None, page2_list=None):
    total_list = page1_list + page2_list
    page1_index = (0, len(page1_list))
    page2_index = (len(page1_list)+1, len(total_list))

    length_list = [
        70, 75, 115, 115, 105, 95, 95, 95, 95, 40, 40,
        60, 70, 70, 70, 65, 50, 75, 75, 65, 75, 265
    ]
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
        for j, k in zip(total_list, length_list):
            length = len(str(i.get(j, '')))
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
            # del temp_height_list[len(temp_height_list) - 1]
            # del temp_height_list[len(temp_height_list) - 1]
            # del temp_list[len(temp_list) - 1]
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
        val = {
            "record_start":min(i),
            "record_end":max(i),
            "page_lengths":j
        }
        index_list.append(val)
    return index_list

page_chunk(gSheetData, page1_list=page1_headers, page2_list=page2_headers)
##Writing the html file
with open('Logbook_Print.html', 'w') as writer:
    # Initialize page write functions
    pw_init = pageWriteFunctions(writer=writer)

    # Determine the chunking
    ##Dividing the dictionaries to pages
    page1_headers = ['DATE', 'AIRCRAFT MAKE AND MODEL', 'AIRCRAFT IDENT',
                  'FROM', 'TO', 'TOTAL DURATION OF FLIGHT', 'AIRPLANE SINGLE-ENGINE LAND',
                  'AIRPLANE SINGLE-ENGINE SEA', 'AIRPLANE MULTI-ENGINE LAND',
                  'LANDINGS DAY', 'LANDINGS NIGHT']

    page2_headers = ['NIGHT', 'ACTUAL INSTRUMENT', 'SIMULATED INSTRUMENT (HOOD)', 'FLIGHT SIMULATOR',
                  'CROSS COUNTRY', 'SOLO', 'PILOT IN COMMAND', 'SECOND IN COMMAND',
                  'DUAL RECEIVED', 'AS FLIGHT INSTRUCTOR', 'REMARKS AND ENDORSEMENTS']

    index_list = pw_init.page_chunk(gSheetData, page1_list=page1_headers, page2_list=page2_headers)

    #Preparing the data for write to the html table
    page1_dict = pw_init.page_divide(page1_headers, data_dict)
    page2_dict = pw_init.page_divide(page2_headers, data_dict)

    #Using the functions to write out to an html table
    ##Starting dictionary
    prev1_totals = {}
    prev2_totals = {}
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
        # Set up the data inputs needed
        start = i['record_start']
        end = i['record_end']+1
        row_heights = i['page_lengths']
        cut_data = data.loc[start:end]
        cut_dict1 = page1_dict[start:end]
        cut_dict2 = page2_dict[start:end]
        year = pw_init.year_compute(cut_dict1)

        # Write the page
        pw_init.p1header_row(page1_headers, year)
        prev = pw_init.page_write(row_heights, cut_data, cut_dict1, page1_headers, prev1_totals, page=1)
        prev1_totals = prev
        pw_init.p2header_row(page2_headers)
        prev = pw_init.page_write(row_heights, cut_data, cut_dict2, page2_headers, prev2_totals, page=2)
        prev2_totals = prev
    writer.write('</body>')
    writer.write('</html>')
writer.close()
