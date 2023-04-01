#!/usr/bin/python3

import os
import csv
import json
import time
import datetime
import calendar
import sys
import getopt

# todo
# Kommentare in mapping csv file zulassen (start mit (#)
# sumi, sume evtl raus?
# correct daily/monthly totals

FieldNamesDaily = ['TimeStamp',              # 0
                   'Bezug',                  # 1
                   'Einspeisung',            # 2
                   'PV',                     # 3
                   'LP1',                    # 4
                   'LP2',                    # 5
                   'LP3',                    # 6
                   'LPGesamt',               # 7
                   'Speicher_Import',        # 8
                   'Speicher_Export',        # 9
                   'Verbraucher1_Import',    # 10
                   'Verbraucher1_Export',    # 11
                   'Verbraucher2_Import',    # 12
                   'Verbraucher2_Export',    # 13
                   'f14',                    # 14
                   'LP4',                    # 15
                   'LP5',                    # 16
                   'LP6',                    # 17
                   'LP7',                    # 18
                   'LP8',                    # 19
                   'SpeicherSOC',            # 20
                   'SOCLP1',                 # 21
                   'SOCLP2',                 # 22
                   'Temp1',                  # 23
                   'Temp2',                  # 24
                   'Temp3',                  # 25
                   'SmartHomeDevice1',       # 26
                   'SmartHomeDevice2',       # 27
                   'SmartHomeDevice3',       # 28
                   'SmartHomeDevice4',       # 29
                   'SmartHomeDevice5',       # 30
                   'SmartHomeDevice6',       # 31
                   'SmartHomeDevice7',       # 32
                   'SmartHomeDevice8',       # 33
                   'SmartHomeDevice9',       # 34
                   'SmartHomeDevice10',      # 35
                   'Temp4',                  # 36
                   'Temp5',                  # 37
                   'Temp6']                  # 38

FieldNamesMonthly = ['TimeStamp',            # 0
                     'Bezug',                # 1
                     'Einspeisung',          # 2
                     'PV',                   # 3
                     'LP1',                  # 4
                     'LP2',                  # 5
                     'LP3',                  # 6
                     'LPGesamt',             # 7
                     'Speicher_Import',      # 8
                     'Speicher_Export',      # 9
                     'Verbraucher1_Import',  # 10
                     'Verbraucher1_Export',  # 11
                     'Verbraucher2_Import',  # 12
                     'Verbraucher2_Export',  # 13
                     'f14',                  # 14
                     'LP4',                  # 15
                     'LP5',                  # 16
                     'LP6',                  # 17
                     'LP7',                  # 18
                     'SmartHomeDevice1',     # 19
                     'SmartHomeDevice2',     # 20
                     'SmartHomeDevice3',     # 21
                     'SmartHomeDevice4',     # 22
                     'SmartHomeDevice5',     # 23
                     'SmartHomeDevice6',     # 24
                     'SmartHomeDevice7',     # 25
                     'SmartHomeDevice8',     # 26
                     'SmartHomeDevice9',     # 27
                     'SmartHomeDevice10']    # 28


def add_one_month(orig_date):
    # advance year and month by one month
    new_year = orig_date.year
    new_month = orig_date.month + 1
    # note: in datetime.date, months go from 1 to 12
    if new_month > 12:
        new_year += 1
        new_month -= 12

    last_day_of_month = calendar.monthrange(new_year, new_month)[1]
    new_day = min(orig_date.day, last_day_of_month)

    return orig_date.replace(year=new_year, month=new_month, day=new_day)

def entryMap(obj: dict, maps: list, row: dict):
    sumi = 0
    sume = 0
    for map in maps:
        if map['devicetype'] not in obj:
            obj[map['devicetype']] = {}
            sumi = 0
            sume = 0
        if map['device'] not in obj[map['devicetype']]:
            obj[map['devicetype']][map['device']] = {}
        if map['conversion'] == 'int' and 'sum' not in map['source']:
            try:
                obj[map['devicetype']][map['device']][map['direction']] = int(float(row[map['source']]))
                if map['direction'] == 'imported' and map['device'] != 'all':
                    sumi = sumi + int(float(row[map['source']]))
                if map['direction'] == 'exported' and map['device'] != 'all':
                    sume = sume + int(float(row[map['source']]))
            except Exception:
                obj[map['devicetype']][map['device']][map['direction']] = int(0)
        if map['conversion'] == 'float':
            try:
                obj[map['devicetype']][map['device']][map['direction']] = float(row[map['source']])
                if map['direction'] == 'imported' and map['device'] != 'all':
                    sumi = sumi + float(row[map['source']])
                if map['direction'] == 'exported' and map['device'] != 'all':
                    sume = sume + float(row[map['source']])
            except Exception:
                obj[map['devicetype']][map['device']][map['direction']] = float(0)
        if map['conversion'] == 'const':
            obj[map['devicetype']][map['device']][map['direction']] = int(map['source'])
        if map['source'] == 'sumi':
            obj[map['devicetype']][map['device']][map['direction']] = sumi
        if map['source'] == 'sume':
            obj[map['devicetype']][map['device']][map['direction']] = sume


def totalsMap(Mode: str, obj: dict, maps: list, entries: list, nextEntry: dict):

    for map in maps:
        if map['devicetype'] not in obj:
            obj[map['devicetype']] = {}
        if map['device'] not in obj[map['devicetype']]:
            obj[map['devicetype']][map['device']] = {}
        if map['conversion'] == 'int' and 'sum' not in map['source']:
            obj[map['devicetype']][map['device']][map['direction']] = int(
                float(nextEntry[map['devicetype']][map['device']][map['direction']]) -
                float(entries[0][map['devicetype']][map['device']][map['direction']]))
        if map['conversion'] == 'float' and 'sum' not in map['source']:
            # if map['devicetype'] == 'pv' and map['direction'] == 'exported':
                # print("pv-totals:" + str(float(nextEntry[map['devicetype']][map['device']][map['direction']])) + ', ' + str(float(entries[0][map['devicetype']][map['device']][map['direction']])))
            obj[map['devicetype']][map['device']][map['direction']]\
             = float(nextEntry[map['devicetype']][map['device']][map['direction']])\
             - float(entries[0][map['devicetype']][map['device']][map['direction']])
        if map['conversion'] == 'const':
            obj[map['devicetype']][map['device']][map['direction']] = int(map['source'])


# Function to convert a CSV to JSON
# Takes the file paths as arguments
def make_json(Mode: str, csvFilePath: str, jsonFilePath: str, mapFile: str):

    if Mode == "D":
        FieldNames = FieldNamesDaily
        # print("dt=" + dt)
    elif Mode == "M":
        FieldNames = FieldNamesMonthly

    dt = os.path.basename(csvFilePath)[0:-4]
    # create dictionaries
    data = {}
    entries = []
    totals = {}

    mapf = open(mapFile, encoding='utf-8')
    mapReader = csv.DictReader(mapf)
    maps = []
    for map in mapReader:
        maps.append(map)

    # Open a csv reader called DictReader
    with open(csvFilePath, encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf, fieldnames=FieldNames)

        # Convert each row into a dictionary
        # and add it to data
        for rows in csvReader:

            entry = {}
            ts = rows['TimeStamp']
            if Mode == 'D':
                tsx = dt + ' ' + ts
                ts_time = time.strptime(tsx, '%Y%m%d %H%M')
                ts = ts[0:2] + ':' + ts[2:4]
            elif Mode == 'M':
                ts_time = time.strptime(ts, '%Y%m%d')
            ts_epoch = int(time.mktime(ts_time))
            entry['timestamp'] = ts_epoch
            entry['date'] = ts

            # print("ts=" + ts + ", epoch=" + ts_epoch + ", t1=" + t1)
            entryMap(entry, maps, rows)
            # print('entry: ' + json.dumps(entry))
            entries.append(entry)

    # for now and as fallback use last row in current file
    # correct would be to use 1st row of next file
    # next file precedence: json file if exists, otherwise csv file from 1.9
    # name of next interval - daily or monthly
    if Mode == 'D':
        act_day = datetime.datetime.strptime(dt, '%Y%m%d')
        next_day = act_day + datetime.timedelta(days=1)
        nextFile = datetime.datetime.strftime(next_day, "%Y%m%d")
    if Mode == 'M':
        act_month = datetime.datetime.strptime(dt, '%Y%m')
        next_month = add_one_month(act_month)
        nextFile = datetime.datetime.strftime(next_month, "%Y%m")

    # search for json file
    next_jsonFile = os.path.dirname(jsonFilePath) + '/' + nextFile + ".json"
    next_csvFile = os.path.dirname(csvFilePath) + '/' + nextFile + ".csv"
    # print("next_jsonFile=" + next_jsonFile + ", next_csvFile=" + next_csvFile)
    if os.path.exists(next_csvFile):
        print("reading next csv file=" + next_csvFile)
        with open(next_csvFile, 'r', encoding='utf-8') as csvf:
            next_csvReader = csv.DictReader(csvf, fieldnames=FieldNames)
            next_entries = []
            for rows in next_csvReader:
                entry = {}
                ts = rows['TimeStamp']
                if Mode == 'D':
                    tsx = dt + ' ' + ts
                    ts_time = time.strptime(tsx, '%Y%m%d %H%M')
                    ts = ts[0:2] + ':' + ts[2:4]
                elif Mode == 'M':
                    ts_time = time.strptime(ts, '%Y%m%d')
                ts_epoch = int(time.mktime(ts_time))
                entry['timestamp'] = ts_epoch
                entry['date'] = ts

                # print("ts=" + ts + ", epoch=" + ts_epoch + ", t1=" + t1)
                entryMap(entry, maps, rows)
                next_entries.append(entry)
            nextEntry = next_entries[0]
    elif os.path.exists(next_jsonFile):
        # print("reading next json file=" + next_jsonFile)
        with open(next_jsonFile, 'r', encoding='utf-8') as jsonf:
            next_json = json.load(jsonf)
            # print("next_json=" + json.dumps(next_json, indent=4))
            nextEntry = next_json['entries'][0]
    else:   
        entries_last = len(entries) - 1
        nextEntry = entries[entries_last]
    totalsMap(Mode, totals, maps, entries, nextEntry)

    # build data dict
    data['entries'] = entries
    data['totals'] = totals

    # Open a json writer, and use the json.dumps()
    # function to dump data
    with open(jsonFilePath, 'w', encoding='utf-8') as jsonf:
        jsonf.write(json.dumps(data, indent=4))


def run_conv(Mode: str, csvFilePath: str, jsonFilePath: str, mapFile: str):

    with os.scandir(csvFilePath) as it:
        for entry in it:
            if entry.name.endswith(".csv") and entry.is_file():
                csvFile = entry.path
                jsonFile = jsonFilePath + '/' + entry.name.replace(".csv", ".json")
                # print("csv-file: " + csvFile + ", jsonFile: " + jsonFile)
                if not os.path.exists(jsonFile):
                    print("convert: csv-file: " + entry.name + ", jsonFile: " + os.path.basename(jsonFile))
                    # Call the make_json function
                    make_json(Mode, csvFile, jsonFile, mapFile)


def main(argv: dict):

    opts, args = getopt.getopt(argv, "hM:m:c:j:", ["Mode=", "mapfile=", "csvfile=", "jsonfile="])
    for opt, arg in opts:
        if opt == '-h':
            print('conv-daily.py -M [D,M] -m <mapfile> -c <csvfile> -j <jsonfile>')
            sys.exit()
        elif opt in ("-M", "--Mode"):
            Mode = arg
        elif opt in ("-m", "--mapfile"):
            mapFile = arg
        elif opt in ("-c", "--csvfile"):
            csvFilePath = arg
        elif opt in ("-j", "--jsonfile"):
            jsonFilePath = arg

    if Mode == 'D' or Mode == 'M':
        # print ('Mode is ', Mode)
        # print ('Map file is ', mapFile)
        # print ('csv file path is ', csvFilePath)
        # print ('json file path is ', jsonFilePath)
        run_conv(Mode, csvFilePath, jsonFilePath, mapFile)
    else:
        print("Mode not in (D,M) - Abort")


if __name__ == "__main__":
    main(sys.argv[1:])
