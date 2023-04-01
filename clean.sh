#!/bin/bash
# remove all files, adjust files as required
cd daily_log
rm 2021* 2020*
rm 20220[1-6]*.json
rm 202207[1-7].json
cd ..
cd monthly_log
rm 2021* 2020* 20220[1-6].json


