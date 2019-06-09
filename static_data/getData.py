# -*- coding: utf-8 -*-
from ConfigParser import ConfigParser
import requests
import os.path
import os

config = ConfigParser()
config.read('../../settings.ini')



status = 'https://api.resrobot.se/samtrafiken/gtfs/feed_info.txt'
gtfsfile = 'https://api.resrobot.se/gtfs/sweden.zip'
stopdata = 'https://api.trafiklab.se/v2/samtrafiken/gtfs/extra/agency_stops.txt'

if os.path.isfile('feed_info.txt'):
    with open('feed_info.txt', 'r') as file:
        current = file.read()
else:
    current = ""

r = requests.get(status, params={"key":config.get("gtfs2","key")})
if not r.content == current:
    print "New feed"
    open('feed_info.txt', 'wb').write(r.content)
    
    print "Getting gtfs file"
    r = requests.get(gtfsfile, params={"key":config.get("gtfs2","key")})
    open('sweden.zip', 'wb').write(r.content)

    print "Getting operator stops id"
    r = requests.get(stopdata, params={"key":config.get("gtfs2","key")})
    open('agency_stops.txt', 'wb').write(r.content)
    print os.popen('unzip -o sweden.zip')
