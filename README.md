# Data Migration from openWB 1.9 to openWB 2.0

This repository contains a python program which migrates data from openWB 1.9 to 2.0.
It needs to be installed rsp. cloned on the system running openWB 2.0.
A Backup of the system is recommmended before running the migration.

openWB 1.9 uses csv file format
openWB 2.0 uses json format

Therefore a field mapping is required.
The field names for 1.9 (daily, monthly) can be found in the source conv.py.

The fields in 2.0 can be found in MQTT e.g. via MQTT-Explorer.
The topics to search for are e.g. "openWB/system/device/<device-no>/component/<component-no>".

The mapping happend by the fieldmap-daily.csv rsp fieldmap-monthlöy.csv files.
These may need adjustment to the devices existing in 1.9 rsp. 2.0.
Each mapping (row) in these files corresponds to a target field in 2.0.
column 1.3 give the address in the 2.0 data structure.
column 4 defines the source in 1.9 or a constant value.
column 5 defines the type of conversion to be applied.
conversion types supported are int, float, const.

daily.sh runs the mogration for all daily files,
monthly.sh for all monthly files.
clean.sh is an example and will need adjustments, it removes the mograted json files.
download_logs.sh copies all log files from openwb 1.9.
_

