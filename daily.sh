#!/bin/bash

# migrate daily files to oowb2
owb19_data_folder=$HOME/conv-logs/data19
daily_logs_19=$owb19_data_folder/daily
daily_logs_20=$HOME/conv-logs/daily_log

./conv.py -M D -m fieldmap-daily.csv -c $daily_logs_19 -j $daily_logs_20

