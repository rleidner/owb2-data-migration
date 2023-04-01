#!/bin/bash
cd daily_log
ls -ltr 2022* | grep "Mar" | awk '{print $9}' | xargs rm
rm 2021* 2020*
cd ..
cd monthly_log
rm 2021* 2020* 20220[1-6].json


