# -*- coding: utf-8 -*-
import sqlite3

stops = sqlite3.connect('stops')
stops.execute("CREATE TABLE IF NOT EXISTS stops(stop_id INT, stop_name TEXT ,stop_lat REAL, stop_lon REAL, stop_scbid TEXT);")
stops.execute("CREATE UNIQUE INDEX IF NOT EXISTS id ON stops(stop_id);")
stops.execute("CREATE TABLE IF NOT EXISTS astops(agency_id INT,stop_id INT, agency_stop_id INT);")
stops.execute("CREATE INDEX IF NOT EXISTS aid ON astops(agency_id, stop_id);")
stops.execute("CREATE TABLE IF NOT EXISTS stop_times(trip_id INT,arrival_time TEXT,departure_time TEXT,stop_id INT,stop_sequence INT,pickup_type INT,drop_off_type INT);")
stops.execute("CREATE INDEX IF NOT EXISTS tid ON stop_times(trip_id);")
stops.execute("CREATE TABLE IF NOT EXISTS trips(route_id INT,service_id INT,trip_id INT,trip_headsign TEXT,trip_short_name TEXT);")
stops.execute("CREATE INDEX IF NOT EXISTS rid ON  trips(route_id);")
stops.execute("CREATE TABLE IF NOT EXISTS routes(route_id INT,agency_id INT,route_short_name TEXT,route_long_name TEXT,route_type INT,route_url TEXT);")
stops.execute("CREATE INDEX IF NOT EXISTS ragency_id ON routes(agency_id);")
stops.execute("CREATE TABLE IF NOT EXISTS akstops(agency_id INT, agency_stop_name TEXT, stop_lat REAL, stop_lon REAL, agency_stop_id INT);")
stops.execute("CREATE INDEX IF NOT EXISTS op ON akstops(agency_id);")
stops.execute("CREATE INDEX IF NOT EXISTS aid ON astops(agency_id, stop_id);")
stops.execute("CREATE TABLE IF NOT EXISTS orter(ort_kommun_scbid INT, ort_scbid TEXT, ort_name TEXT, ort_lat REAL, ort_lon REAL);")
stops.execute("CREATE UNIQUE INDEX IF NOT EXISTS oid ON orter(ort_scbid);")
stops.execute("DELETE FROM stops;")
stops.execute("DELETE FROM astops;")
stops.execute("VACUUM")
print "sqlite3 stops"
print '.separator ","'
print '.import exstops.txt stops'
print '.import agency_stops.txt astops'
print '.import stop_times.txt stop_times'
print '.import trips.txt trips'
print '.import routes.txt routes'
print '.separator "|"'
print '.import orter.txt orter'