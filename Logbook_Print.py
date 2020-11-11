# @Author: katie
# @Date:   2017-07-09T19:41:52-05:00
# @Last modified by:   katie
# @Last modified time: 2020-11-10T20:37:46-06:00



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
import json

from core.Drive_Data_Fetch import googleSpreadsheetFetch
from core.Page_Write_Functions import pageWriteFunctions

# Get data from drive
gDrive_init = googleSpreadsheetFetch(
    scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly'],
    client_secret_file = 'client_secret.json',
    authorization_file = 'token.pickle',
    spreadsheetId = '15FeoThcHzYceUEoIR6uegF4HFH-jJKzW6paitZ9dipM',
    rangeName = 'XJT_Logbook_CLEAN!B:AK',
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
    'COMPLEX': 0.0,
    'TURBINE SIC': 0.0,
    'TURBINE PIC': 0.0,
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
    'COMPLEX':'{:,.1f}',
    'TURBINE SIC':'{:,.1f}',
    'TURBINE PIC':'{:,.1f}',
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

data_dict = data_formatted.to_dict(orient='records')

# Look for address information...Populate if needed
gDrive_init.getName_Address('Address.json')

# Get the address information
address_file = open('Address.json', 'r')
address_info = json.load(address_file)

##Writing the html file
with open('Logbook_Print.html', 'w') as writer:
    # Initialize page write functions
    pw_init = pageWriteFunctions(writer=writer)

    # Determine the chunking
    ##Dividing the dictionaries to pages
    page1_headers = ['DATE', 'AIRCRAFT MAKE AND MODEL', 'AIRCRAFT IDENT',
                  'FROM', 'TO', 'TOTAL DURATION OF FLIGHT', 'AIRPLANE SINGLE-ENGINE LAND',
                  'AIRPLANE SINGLE-ENGINE SEA', 'AIRPLANE MULTI-ENGINE LAND', 'COMPLEX',
                  'TURBINE SIC', 'TURBINE PIC', 'LANDINGS DAY', 'LANDINGS NIGHT']

    page2_headers = ['NIGHT', 'ACTUAL INSTRUMENT', 'SIMULATED INSTRUMENT (HOOD)', 'FLIGHT SIMULATOR',
                  'CROSS COUNTRY', 'SOLO', 'PILOT IN COMMAND', 'SECOND IN COMMAND',
                  'DUAL RECEIVED', 'AS FLIGHT INSTRUCTOR', 'REMARKS AND ENDORSEMENTS']

    index_list = pw_init.page_chunk(data_dict, page1_list=page1_headers, page2_list=page2_headers, char_pxl_width=7)

    #Preparing the data for write to the html table
    page1_dict = pw_init.page_divide(page1_headers, data_dict)
    page2_dict = pw_init.page_divide(page2_headers, data_dict)

    # Getting the dates for the title page
    title_dates = pw_init.logbook_dates(data['DATE'])

    #Using the functions to write out to an html table
    ##Starting dictionary
    prev1_totals = {}
    prev2_totals = {}
    for i in index_list:
        # Set up the data inputs needed
        start = i['record_start']
        end = i['record_end']
        row_heights = i['page_lengths']
        cut_data = data.loc[start:end]
        cut_dict1 = page1_dict[start:end+1]
        cut_dict2 = page2_dict[start:end+1]
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

# Prepend the file with the title page information
# Get the total flight time
totals = prev1_totals
totals.update(prev2_totals)
totals['TOTAL TURBINE'] = totals['TURBINE PIC'] + totals['TURBINE SIC']

with open('Logbook_Print.html', 'r+') as writer:
    content = writer.read()
    writer.seek(0,0)
    writer.write(
        f"""
        <html>
        <head>
        <link rel="stylesheet" href="style.css">
        <head>
        <title>{address_info['name']} Logbook</title>
        <body>
        <br>
        <br>
        <h1>Flight Record</h1>
        <p>for</p>
        <h2>{address_info['name']}</h2>
        <h5>{address_info['address']}</h5>
        <h5>{address_info['city_state']}</h5>
        <p><b>Phone:<b>{address_info['phone']}</p>
        <p><a href="mailto:email@gmail.com">{address_info['email']}</a></p>
        """
    )
    writer.write('<h3>Logbook from {0} to {1}</h3>'.format(title_dates[0], title_dates[1]))
    writer.write('<h3>Summary of Total Time</h3>')
    writer.write(f"""
        <table class=titlepage>
            <col width="150">
            <col width="50">
            <col width="150">
            <col width="50">
            <tr>
                <td><b>Total Flight Time</b></td>
                <td>{totals['TOTAL DURATION OF FLIGHT']:.1f}</td>
                <td><b>Simulated Instrument</b></td>
                <td>{totals['SIMULATED INSTRUMENT (HOOD)']:.1f}</td>
            </tr>
            <tr>
                <td><b>Pilot in Command</b></td>
                <td>{totals['PILOT IN COMMAND']:.1f}</td>
                <td><b>Actual Instrument</b></td>
                <td>{totals['ACTUAL INSTRUMENT']:.1f}</td>
            </tr>
            <tr>
                <td><b>Second in Command</b></td>
                <td>{totals['SECOND IN COMMAND']:.1f}</td>
                <td><b>Night</b></td>
                <td>{totals['NIGHT']:.1f}</td>
            </tr>
            <tr>
                <td><b>Total Turbine</b></td>
                <td>{round(totals['TOTAL TURBINE'],1):.1f}</td>
                <td><b>Cross Country</b></td>
                <td>{totals['CROSS COUNTRY']:.1f}</td>
            </tr>
            <tr>
                <td><b>Multi-Engine</b></td>
                <td>{totals['AIRPLANE MULTI-ENGINE LAND']:.1f}</td>
                <td><b>Dual Given</b></td>
                <td>{totals['DUAL RECEIVED']:.1f}</td>
            </tr>
        </table>
    <div class="pagebreak"> </div>
    <h1>Notes</h1>
    <div class="pagebreak"> </div>
    <h1>Notes</h1>
    <div class="pagebreak"> </div>
    """)
    writer.write(content)
writer.close()
