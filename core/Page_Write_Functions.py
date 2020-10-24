# @Author: katie
# @Date:   2020-10-22T19:46:50-05:00
# @Last modified by:   katie
# @Last modified time: 2020-10-24T11:08:06-05:00

import numpy as np
from datetime import datetime


class pageWriteFunctions(object):
    """docstring for pageWriteFunctions."""

    def __init__(self, writer=None):
        self.writer = writer

    ##Function that writes out the year for the header of the table
    @staticmethod
    def year_compute(input_dict):
        temp_list = list()
        for record in input_dict:
            date = datetime.strptime(record['DATE'], '%M/%d/%Y').date().strftime('%Y')
            if date in temp_list:
                continue
            temp_list.append(date)
        if len(temp_list) == 1:
            year = temp_list[0]
        else:
            year = '/'.join(temp_list)
        return year

    ##Defining the header row and the fixed widths of the columns - page even

    def p1header_row(self, values, year):
        self.writer.write('<table class=page1>')
        self.writer.write('<col width="70">')
        self.writer.write('<col width="75">')
        self.writer.write('<col width="115">')
        self.writer.write('<col width="115">')
        self.writer.write('<col width="105">')
        self.writer.write('<col class="gray" width="95">')
        self.writer.write('<col width="95">')
        self.writer.write('<col class= "gray" width="95">')
        self.writer.write('<col width="95">')
        self.writer.write('<col class="gray" width="40">')
        self.writer.write('<col width="40">')
        self.writer.write('<tr>')
        self.writer.write('<th colspan = "3">YEAR ' \
                     + year \
                     + '</th>')
        self.writer.write('<th colspan = "2">ROUTE OF FLIGHT</th>')
        self.writer.write('<th rowspan = "2">TOTAL DURATION OF FLIGHT</th>')
        self.writer.write('<th colspan = "3">AIRCRAFT CATEGORY AND CLASS</th>')
        self.writer.write('<th colspan = "2">LANDINGS</th>')
        self.writer.write('</tr><tr>')
        for i in values:
            if i == 'TOTAL DURATION OF FLIGHT':
                continue
            elif 'LANDINGS' in i:
                i = i.split(' ')[1]
            j = '<th class=secondrow>' + i + '</th>'
            self.writer.write(j)
        self.writer.write('</tr>')

    ##Defining the header row and fixed widths of the columns - page odd
    def p2header_row(self, values):
        self.writer.write('<table class=page2>')
        self.writer.write('<col class="gray" width="60">')
        self.writer.write('<col width="70">')
        self.writer.write('<col class="gray" width="70">')
        self.writer.write('<col width="70">')
        self.writer.write('<col class="gray" width="65">')
        self.writer.write('<col width="50">')
        self.writer.write('<col class="gray" width="75">')
        self.writer.write('<col width="75">')
        self.writer.write('<col class="gray" width="65">')
        self.writer.write('<col width="75">')
        self.writer.write('<col width="265">')
        self.writer.write('<tr>')
        self.writer.write('<th colspan = "3">CONDITIONS OF FLIGHT</th>')
        self.writer.write('<th rowspan = "2">FLIGHT SIMULATOR</th>')
        self.writer.write('<th colspan = "6">TYPE OF PILOTING TIME</th>')
        self.writer.write('<th rowspan = "2">REMARKS AND ENDORSEMENTS</th>')
        self.writer.write('</tr><tr>')
        for i in values:
            if i == 'FLIGHT SIMULATOR':
                continue
            elif i == 'REMARKS AND ENDORSEMENTS':
                continue
            j = '<th class=secondrow>' + i + '</th>'
            self.writer.write(j)
        self.writer.write('</tr>')

    ##Function that develops the page1 and page2 dictionaries
    @staticmethod
    def page_divide(header_list, input_dict):
        output_dict = list()
        for i in input_dict:
            dict1 = dict()
            for key, value in iter(i.items()):
                if key in header_list:
                    dict1[key] = value
                else:
                    continue
            output_dict.append(dict1)
        return output_dict

    ##Function that dynamically defines the pages
    @staticmethod
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
            val = {
                "record_start":min(i),
                "record_end":max(i),
                "page_lengths":j
            }
            index_list.append(val)
        return index_list

    # Getting the sums
    @staticmethod
    def get_totals(data, columns, prev_totals):
        column_totals = {}
        combined_totals = {}
        for i in columns:
            if i not in ['DATE', 'AIRCRAFT MAKE AND MODEL', 'AIRCRAFT IDENT',
                         'FROM', 'TO', 'APPROACH', 'REMARKS AND ENDORSEMENTS']:
                if i in ['LANDINGS DAY', 'LANDINGS NIGHT']:
                    column_totals[i] = int(round(data[i].sum(), 0))
                    combined_totals[i] = int(round(prev_totals.get(i, 0) + column_totals[i], 0))
                else:
                    column_totals[i] = round(data[i].sum(), 1)
                    combined_totals[i] = round(prev_totals.get(i, 0) + column_totals[i], 1)
            else:
                column_totals[i] = ''
                combined_totals[i] = ''

        return {
            'curr_totals':column_totals,
            'combined_totals':combined_totals
            }

    # Writing out the page body
    def page_write(self, row_height_list, cut_df, formatted_dict, input_headers, prev_totals, page):
        page_totals = self.get_totals(cut_df, input_headers, prev_totals)
        curr_totals = page_totals['curr_totals']
        combined_totals = page_totals['combined_totals']
        for val, height in zip(formatted_dict, row_height_list):
            self.writer.write('<tr>')
            for col in input_headers:
                cell = '<td style="height:' + str(height) + 'px;">' + val.get(col, ' ') + '</td>'
                self.writer.write(cell)
            self.writer.write('</tr>')
        if page == 1:
            for m, n in zip(
                [curr_totals, prev_totals, combined_totals],
                ['TOTALS THIS PAGE', 'AMT. FORWARDED', 'TOTALS TO DATE']
            ):
                if n == 'TOTALS THIS PAGE':
                    self.writer.write('<tr>')
                    self.writer.write('<th class="p1box" colspan="2" rowspan = "4">Totals</th>')
                    self.writer.write('</tr>')
                self.writer.write('<tr>')
                self.writer.write('<td class="boldcenter" colspan="3">' + n + ' </td>')
                for k in input_headers:
                    if k in ['DATE', 'AIRCRAFT MAKE AND MODEL', 'AIRCRAFT IDENT', 'FROM',
                             'TO']:
                        continue
                    else:
                        self.writer.write('<td>' + str(m.get(k, 0)) + '</td>')
            self.writer.write('</tr>')
        elif page == 2:
            for m, n in zip(
                [curr_totals, prev_totals, combined_totals],
                ['TOTALS THIS PAGE', 'AMT. FORWARDED', 'TOTALS TO DATE']
            ):
                self.writer.write('<tr>')
                for l in input_headers:
                    if l == 'REMARKS AND ENDORSEMENTS' and n == 'TOTALS THIS PAGE':
                        self.writer.write('<th class="p2box" rowspan="4" align="center" style="font-size: 9px;">I certify that the entries in this ' + \
                                     'log are true<br><br>____________________________________' + \
                                     '<br>PILOT SIGNATURE</th>')
                    elif l == 'REMARKS AND ENDORSEMENTS' and n != 'TOTALS THIS PAGE':
                        continue
                    else:
                        self.writer.write('<td>' + str(m.get(l, 0)) + '</td>')
                self.writer.write('</tr>')
        self.writer.write('</table>')

        return combined_totals
