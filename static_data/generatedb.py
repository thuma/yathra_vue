# -*- coding: utf-8 -*-
import sqlite3

stops = sqlite3.connect('stops')
stops.execute("CREATE TABLE IF NOT EXISTS stops(stop_id INT, stop_name TEXT ,stop_lat REAL, stop_lon REAL, stop_scbid INT);")
stops.execute("CREATE UNIQUE INDEX IF NOT EXISTS id ON stops(stop_id);")
stops.execute("CREATE TABLE IF NOT EXISTS astops(agency_id INT,stop_id INT, agency_stop_id INT);")
stops.execute("CREATE INDEX IF NOT EXISTS aid ON astops(agency_id, stop_id);")
stops.execute("DELETE FROM stops;")
stops.execute("DELETE FROM astops;")
stops.execute("VACUUM")
print "sqlite3 stops"
print '.separator ","'
print '.import exstops.txt stops'
print '.import agency_stops.txt astops'