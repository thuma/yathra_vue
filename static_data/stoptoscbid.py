# -*- coding: utf-8 -*-
import json
from shapely.geometry import shape, Point
import csv
# depending on your version, use: from shapely.geometry import shape, Point

# load GeoJSON file containing sectors
with open('kommun.geojson') as f:
    js = json.load(f)

with open('exstops.txt', 'w') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    with open('stops.txt', 'r') as stops:
        csvreader = csv.reader(stops, delimiter=',', quotechar='"')
        for stop in csvreader:
            try:
                print stop[1]
                point = Point(float(stop[3]), float(stop[2]))
            except:
                print "error"
                continue
            # check each polygon to see if it contains the point
            for feature in js['features']:
                polygon = shape(feature['geometry'])
                if polygon.contains(point):
                    stop[4] = feature.get('properties').get('KOM_KOD')
                    break
            csvwriter.writerow(stop)
