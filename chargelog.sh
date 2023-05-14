#!/bin/bash

# migrate chargelog files to owb2 format
owb19_data_folder=$HOME/conv-logs/data19
ladelogs_19=$owb19_data_folder/ladelog
charge_logs_20=$HOME/conv-logs/charge_log

./conv.py -M L -m fieldmap-chargelog.csv -c $ladelogs_19 -j $charge_logs_20 -C chargemap.csv

