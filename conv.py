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

FieldNamesChargelog = ['Startzeit',          # 1
                       'Endzeit',            # 2
                       'geladene_km',        # 3
                       'geladene_kWh',       # 4
                       'Ladeleistung_kW',    # 5
                       'Ladedauer',          # 6
                       'Ladepunkt_Nummer',   # 7
                       'Lademodus',          # 8
                       'RFID_Tag',           # 9
                       'Kosten']             # 10


def readCsv(csvFile: str, csvs: list):
    csvf = open(csvFile, encoding='utf-8')
    csvReader = csv.DictReader(csvf)
    for csvrow in csvReader:
        csvs.append(csvrow)


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
    for map in maps:
        if map['devicetype'] not in obj:
            obj[map['devicetype']] = {}
        if map['device'] not in obj[map['devicetype']]:
            obj[map['devicetype']][map['device']] = {}
        if map['conversion'] == 'int':
            try:
                obj[map['devicetype']][map['device']][map['direction']] = int(float(row[map['source']]))
            except Exception:
                obj[map['devicetype']][map['device']][map['direction']] = int(0)
        if map['conversion'] == 'float':
            try:
                obj[map['devicetype']][map['device']][map['direction']] = float(row[map['source']])
            except Exception:
                obj[map['devicetype']][map['device']][map['direction']] = float(0)
        if map['conversion'] == 'const':
            obj[map['devicetype']][map['device']][map['direction']] = int(map['source'])


def totalsMap(Mode: str, obj: dict, maps: list, entries: list, nextEntry: dict):

    for map in maps:
        if map['devicetype'] not in obj:
            obj[map['devicetype']] = {}
        if map['device'] not in obj[map['devicetype']]:
            obj[map['devicetype']][map['device']] = {}
        if map['conversion'] == 'int':
            obj[map['devicetype']][map['device']][map['direction']] = int(
                float(nextEntry[map['devicetype']][map['device']][map['direction']]) -
                float(entries[0][map['devicetype']][map['device']][map['direction']]))
        if map['conversion'] == 'float':
            obj[map['devicetype']][map['device']][map['direction']]\
             = float(nextEntry[map['devicetype']][map['device']][map['direction']])\
             - float(entries[0][map['devicetype']][map['device']][map['direction']])
        if map['conversion'] == 'const':
            obj[map['devicetype']][map['device']][map['direction']] = int(map['source'])


# read and process 1.9 csv data file into json structure, daily and monthly
def readCsvData(Mode: str, csvFile: str, FieldNames: list, entries: list, dt: str, maps: list):
    # print("reading csv file: " + csvFile)
    with open(csvFile, 'r', encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf, fieldnames=FieldNames)
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
            entries.append(entry)


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

    maps = []
    readCsv(mapFile, maps)

    readCsvData(Mode, csvFilePath, FieldNames, entries, dt, maps)

    # create totals entry
    # 1. use csv file as next entry if existent
    # 2. use csv file as next entry if existent
    # 3. as fallback use last row in current file
    if Mode == 'D':
        act_day = datetime.datetime.strptime(dt, '%Y%m%d')
        next_day = act_day + datetime.timedelta(days=1)
        nextFile = datetime.datetime.strftime(next_day, "%Y%m%d")
    if Mode == 'M':
        act_month = datetime.datetime.strptime(dt, '%Y%m')
        next_month = add_one_month(act_month)
        nextFile = datetime.datetime.strftime(next_month, "%Y%m")

    # search for csv, then for json file
    next_csvFile = os.path.dirname(csvFilePath) + '/' + nextFile + ".csv"
    next_jsonFile = os.path.dirname(jsonFilePath) + '/' + nextFile + ".json"

    if os.path.exists(next_csvFile):
        next_entries = []
        readCsvData(Mode, next_csvFile, FieldNames, next_entries, dt, maps)
        nextEntry = next_entries[0]
    elif os.path.exists(next_jsonFile):
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


# mapping chargelog structure
def entryMapChargelog(obj: dict, maps: list, chargemaps: list, row: dict):
    for map in maps:
        if map['section'] not in obj:
            obj[map['section']] = {}
        if map['item'] not in obj[map['section']]:
            obj[map['section']][map['item']] = None
        if 'map' in map['conversion']:
            try:
                key = map['key']
                o1 = row[map['source']]
                # print("conversion(map): key=" + str(key) + ", o1=" + str(o1))
                # print("chargemaps=" + str(chargemaps))
                cm = list(filter(lambda cmap: cmap['key'] == key and cmap['owb1Value'] == o1, chargemaps))[0]
                # print("cm=" + str(cm))
                o2 = cm['owb2Value']
                # print("conversion(map): key=" + str(key) + ", o1=" + str(o1) + ", o2=" + str(o2))
                if 'str' in map['conversion']:
                    obj[map['section']][map['item']] = o2
                elif 'float' in map['conversion']:
                    obj[map['section']][map['item']] = float(o2)
                elif 'int' in map['conversion']:
                    obj[map['section']][map['item']] = int(float(o2))
            except Exception as e:
                print("exception(map): " + str(e))
                obj[map['section']][map['item']] = 'mapFAILED'
        if map['conversion'] == 'bool':
            try:
                if map['source'] == "true":
                    obj[map['section']][map['item']] = True
                if map['source'] == "false":
                    obj[map['section']][map['item']] = False
            except Exception as e:
                print("exception(map): " + str(e))
        if map['conversion'] == 'timestamp':
            try:
                ts = row[map['source']]
                ts_time = datetime.datetime.strptime(ts, '%d.%m.%y-%H:%M')
                obj[map['section']][map['item']] = datetime.datetime.strftime(ts_time, '%m/%d/%Y, %H:%M:00')
            except Exception as e:
                print("exception(timestamp): " + str(e))
                obj[map['section']][map['item']] = '01/01/1970, 00:00:00'
        if map['conversion'] == 'interval':
            try:
                delta = row[map['source']].replace(' ', '').replace('H',':').replace('Min','')
                if ':' not in delta:
                    delta = '00:' + delta
                obj[map['section']][map['item']] = delta
            except Exception as e:
                print("exception(interval): " + str(e))
                obj[map['section']][map['item']] = '00:00'
        if map['conversion'] == 'int':
            try:
                obj[map['section']][map['item']] = int(float(row[map['source']]))
            except Exception:
                obj[map['section']][map['item']] = int(0)
        if map['conversion'] == 'Mint':
            try:
                obj[map['section']][map['item']] = int(float(row[map['source']]) * 1000)
            except Exception:
                obj[map['section']][map['item']] = int(0)
        if map['conversion'] == 'float':
            try:
                obj[map['section']][map['item']] = float(row[map['source']])
            except Exception:
                obj[map['section']][map['item']] = float(0)
        if map['conversion'] == 'const':
            obj[map['section']][map['item']] = int(map['source'])


# read and process 1.9 csv data file into json structure, chargelog
def readCsvChargelog(csvFile: str, FieldNames: list, entries: list, dt: str, maps: list, chargemaps: list):
    # print("reading csv file: " + csvFile)
    with open(csvFile, 'r', encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf, fieldnames=FieldNames)
        for rows in csvReader:
            entry = {}

            # print("ts=" + ts + ", epoch=" + ts_epoch + ", t1=" + t1)
            entryMapChargelog(entry, maps, chargemaps, rows)
            entries.append(entry)


# Function to convert a CSV to JSON
# Takes the file paths as arguments
def make_json_chargelog(Mode: str, csvFilePath: str, jsonFilePath: str, mapFile: str, chargemapFile: str):
    # print("make_json_chargelog tbd")
    FieldNames = FieldNamesChargelog
    dt = os.path.basename(csvFilePath)[0:-4]
    # create dictionaries
    entries = []

    maps = []
    readCsv(mapFile, maps)
    chargemaps = []
    readCsv(chargemapFile, chargemaps)

    readCsvChargelog(csvFilePath, FieldNames, entries, dt, maps, chargemaps)

    # Open a json writer, and use the json.dumps()
    # function to dump data
    with open(jsonFilePath, 'w', encoding='utf-8') as jsonf:
        jsonf.write(json.dumps(entries, indent=4))


# iterator over all csv files
def run_conv(Mode: str, csvFilePath: str, jsonFilePath: str, mapFile: str, chargemapFile: str):
    with os.scandir(csvFilePath) as it:
        for entry in it:
            if entry.name.endswith(".csv") and entry.is_file():
                csvFile = entry.path
                jsonFile = jsonFilePath + '/' + entry.name.replace(".csv", ".json")
                # print("csv-file: " + csvFile + ", jsonFile: " + jsonFile)
                if not os.path.exists(jsonFile):
                    print("convert: csv-file: " + entry.name + ", jsonFile: " + os.path.basename(jsonFile))
                    if Mode == "D" or Mode == "M":
                        make_json(Mode, csvFile, jsonFile, mapFile)
                    elif Mode == "L":
                        make_json_chargelog(Mode, csvFile, jsonFile, mapFile, chargemapFile)


def main(argv: dict):
    chargemapFile = ''
    opts, args = getopt.getopt(argv, "hM:m:c:j:C:", ["Mode=", "mapfile=", "csvfile=", "jsonfile=", "chargemap="])
    for opt, arg in opts:
        if opt == '-h':
            print('conv-daily.py -M [D,M,L] -m <mapfile> -c <csvfile> -j <jsonfile>')
            sys.exit()
        elif opt in ("-M", "--Mode"):
            Mode = arg
        elif opt in ("-C", "--chargemap"):
            chargemapFile = arg
        elif opt in ("-m", "--mapfile"):
            mapFile = arg
        elif opt in ("-c", "--csvfile"):
            csvFilePath = arg
        elif opt in ("-j", "--jsonfile"):
            jsonFilePath = arg

    if Mode == 'D' or Mode == 'M' or Mode == 'L':
        print ('Mode is ' + Mode)
        print ('Map file is ' + mapFile)
        if Mode == 'L':
            print ('Chargemap file is ' + chargemapFile)
        print ('csv file path is ' + csvFilePath)
        print ('json file path is ' + jsonFilePath)
        if not chargemapFile:
            chargemapFile = ""
        run_conv(Mode, csvFilePath, jsonFilePath, mapFile, chargemapFile)
    else:
        print("Mode not in (D,M,L) - Abort")


if __name__ == "__main__":
    main(sys.argv[1:])
