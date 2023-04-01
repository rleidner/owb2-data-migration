#!/bin/bash

# migrate monthly files to owb2
owb19_data_folder=$HOME/conv-logs/data19
monthly_logs_19=$owb19_data_folder/monthly
monthly_logs_20=$HOME/conv-logs/monthly_log

./conv.py -M M -m fieldmap-monthly.csv -c $monthly_logs_19 -j $monthly_logs_20
