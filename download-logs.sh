#!/bin/bash
url=http://openwb/openWB/web/logging/data/
logs_folder=$HOME/conv-logs/data19
fromMonth=202010

cd $logs_folder
if [ ! -d log ]; then mkdir log; fi

for d in `curl -sS $url | grep "href=" | grep -v "Parent" | grep -v Name | sed 's_.*href="__' | awk -F "/" '{print $1}'`
do
   nurl=$url$d/
#   echo $d, nurl=$nurl
   if [ ! -d $d ]; then mkdir $d; fi
   for f in `curl -sS $nurl | grep "href=" | grep -v "Parent" | grep -v Name | sed 's_.*href="__' | awk -F "/" '{print $1}' | awk -F "\"" '{print $1}'`
   do
     ts=`echo $f | cut -c1-6`
     if [ $ts -ge $fromMonth ]
     then
        echo d=$d, f=$f, ts=$ts 
        echo "wget --output-document=$d/$f --output-file=log/$d.$f.log --timestamping $nurl/$f"
        wget --output-document=$d/$f --output-file=log/$d.$f.log $nurl/$f
        rc=$?
        if [ $rc -ne 0 ]
        then
           echo "wget failed: $nurl/$f , rc=$rc"
        fi
     fi
   done
done


