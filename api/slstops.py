# !/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from ConfigParser import ConfigParser

config = ConfigParser()
config.read('../../settings.ini')

rawdata = requests.get("https://api.sl.se/api2/LineData.json?model=Site&key="+config.get("sl","hplkey"))
arealist = rawdata.json()["ResponseData"]["Result"]
areadict = {}
for area in arealist:
    if len(area["SiteId"]) < 5:
        areadict[area["StopAreaNumber"]] = area["SiteId"]

def getByArea(id):
    return areadict[str(id)]
