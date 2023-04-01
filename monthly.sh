#!/bin/bash
owb19_data_folder=$HOME/conv-logs/data19
monthly_logs_19=$owb19_data_folder/monthly
monthly_logs_20=$HOME/conv-logs/monthly_log

./conv.py -M M -m fieldmap-monthly.csv -c $monthly_logs_19 -j $monthly_logs_20
exit

cd $monthly_logs_19

for f in *.csv
do
    fj=`echo $f | sed 's/.csv/.json/'`
    if [ ! -f $monthly_logs_20/$fj ]
    then
        echo convert $f to $fj
        $wd/conv-monthly.py -m $wd/fieldmap-monthly.csv -c $f -j $monthly_logs_20/$fj
    else
        echo skip $f to $fj
    fi
done

