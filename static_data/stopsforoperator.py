import sqlite3

stops = sqlite3.connect('stops')

query = stops.execute('''
SELECT agency_id, trips.trip_id, stop_times.stop_id, stops.stop_name, stops.stop_lon, stops.stop_lat, stops.stop_scbid
FROM routes 
INNER JOIN trips ON routes.route_id = trips.route_id 
INNER JOIN stop_times ON trips.trip_id = stop_times.trip_id 
INNER JOIN stops ON stop_times.stop_id = stops.stop_id
WHERE agency_id = 261 GROUP BY stop_times.stop_id;''')

for row in query:
    hassstop = 1
    for stop in stops.execute("SELECT * FROM astops WHERE agency_id = 261 AND stop_id = %s" % row[2]):
        hassstop = 0
    if hassstop:
        print row
