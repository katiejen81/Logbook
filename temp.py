#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 21 21:23:09 2017

@author: katie
"""

length_list = [70, 70, 70, 80, 75, 75, 75, 75, 75, 75, 385]
record_rows = 0
temp_list = list()
value_list = list()
info_list = list()
for i in page2_dict:
    index = page2_dict.index(i)
    temp_list.append(index)
    col_rows = list()
    dict1 = dict()
    for j, k in zip(page2_list, length_list):
        length = len(i.get(j, ''))
        length_px = length * 7.5
        if np.ceil(length_px/k) == 0:
            rows = 1
        else:
            rows = int(np.ceil(length_px/k))
        dict1['length'] = length
        dict1['length_px'] = length_px
        dict1['rows'] = rows
        col_rows.append(rows)
    info_list.append(dict1)
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
