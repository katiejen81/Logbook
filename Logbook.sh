# @Author: katie
# @Date:   2018-04-15T16:57:13-05:00
# @Last modified by:   katie
# @Last modified time: 2018-04-15T17:06:29-05:00



#!/bin/bash

cd '/media/katie/322f9f54-fb6e-4d56-b45c-9e2850394428/Katie Programs/Logbook'

source activate logbook

python Logbook_Harvest.py
python Logbook_Print.py

source deactivate logbook
