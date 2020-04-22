# @Author: katie
# @Date:   2018-04-15T16:57:13-05:00
# @Last modified by:   katie
# @Last modified time: 2018-04-15T17:06:29-05:00



#!/bin/bash

cd '/home/mike/apps/Logbook'

conda activate logbook

python Logbook_Harvest.py
python Logbook_Print.py

conda deactivate
