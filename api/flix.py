# !/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, json, sqlite3, datetime, urllib, math
from flixstops import stops
from bottle import get, post, run, request, response
from dateutil import parser, tz
from urllib import urlencode, quote_plus

travelCats = {
    "adult":"Vuxen",
    "children":"Barn 0 till 15 år",
    "bike_slot":"Cyklar"
}

db = sqlite3.connect("stops")

localstops = []
for stop in stops:
  newstop = {"name":stop["name"],"id":stop["id"],"lon":float(stop["lon"]),"lat":float(stop["lat"])}
  if newstop["lat"] > 54.6126051 and newstop["lon"] > 7.5128732 and newstop["lon"] < 26.1078057:
    localstops.append(newstop)

def TimeStampToIso(tstamp):
  return datetime.datetime.fromtimestamp(tstamp).strftime("%Y-%m-%dT%H:%M:%SZ")

def isoToFlexdate(string):
  try:
    utc_dt = datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.%fZ')
  except:
    utc_dt = datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%SZ')
  return utc_dt.strftime("%d.%m.%Y")

def isoToDate(string):
  try:
    utc_dt = datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.%fZ')
  except:
    utc_dt = datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%SZ')
  return utc_dt.strftime("%Y-%m-%d")

def isoToTimeStamp(string):
  try:
    utc_dt = datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.%fZ')
  except:
    utc_dt = datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%SZ')
  return (utc_dt - datetime.datetime(1970, 1, 1)).total_seconds()

def stringToUnixTS(string):
  utc_dt = parser.parse(string).astimezone(tz.tzutc());
  return (utc_dt - datetime.datetime(1970, 1, 1, tzinfo=tz.tzutc())).total_seconds()

def distanse(locationa,locationb):
  return math.sqrt(
  	abs(locationa['lon']-locationb['lon']) + 
  	abs(locationa['lat']-locationb['lat'])
  	)

def StopIdToName(id):
  current = {"dist":9999999}
  for row in db.execute("SELECT stop_lat,stop_lon FROM stops WHERE stop_id = %s" % id):
    position = {
    	"lat":float(row[0]),
    	"lon":float(row[1])
    }
    for stop in localstops:
      stop["dist"] = distanse(position,stop)
      if current["dist"] > stop["dist"]:
        current = stop
  return current

@post('/api/v1/buy')
def cats():
    response.content_type = 'application/json'
    returndata = {"payUrl":"https://tc.tradetracker.net/?c=26525&m=12&a=350004&u="+quote_plus(request.json["productId"])}
    return json.dumps(returndata)

@get('/api/v1/productcat/travellers')
def cats():
    response.content_type = 'application/json'
    return json.dumps(travelCats)

@post('/api/v1/product')
def search():
    search = request.json
    #search = {
    #    "route": [
    #        { "stopId": "740000001" },
    #        { "stopId": "740000002" }
    #    ],
    #    "travellersPerCategory": [
    #        {
    #            "cat": "VU",
    #            "tra": 1,
    #            "age": 35
    #        }
    #    ],
    #    "temporal": {
    #        "earliestDepature": "2019-07-01T12:05:00Z",
    #        "latestArrival": "2019-07-01T16:05:00Z" 
    #    }
    #}

    params = {
        "departureCity":StopIdToName(search["route"][0]["stopId"])["id"],
        "arrivalCity":StopIdToName(search["route"][1]["stopId"])["id"],
        "rideDate":isoToFlexdate(search["temporal"]["earliestDepature"]),
        "_locale":"en"
    }
    
    print params
    
    for traveller in search["travellersPerCategory"]:
        params[traveller['cat']] = traveller['tra']

    result = requests.get(
        "https://shop.flixbus.se/search",
        params=params
        )
    
    jsondata = result.content.split("$('#search-results-wrapper').searchResultFilters(")[1].split("});")[0]
    jsondata = jsondata.split("searchResults:")[1].split("\n")[0].strip()[:-1]
    trips = []
    for trip in json.loads(jsondata)["ridesData"]["direct"]["rides"][isoToDate(search["temporal"]["earliestDepature"])]:
        if trip["departure"] >= stringToUnixTS(search["temporal"]["earliestDepature"]) and trip["arrival"] <= stringToUnixTS(search["temporal"]["latestArrival"]):
            trips.append(trip)
    
    products = []
    for trip in trips:
      pricelist = []
      url = "https://shop.flixbus.se/search?"+urlencode(params);
      for type in ["one"]:
        pris = float(trip["price"])
        pricelist.append({
            "productId": url,
            "productTitle": "Lägsta pris",
            "productDescription": "Enkel biljett",
            "fares": [
                {
                    "amount": pris,
                    "currency": "SEK",
                    "vatAmount": round(pris*0.06,2),
                    "vatPercent": 6
                }
            ],
            "productProperties": {
                "date": trip["departureDateTime"]
            },
            "travellersPerCategory": search["travellersPerCategory"]
        })
      products.append(pricelist)
    response.content_type = 'application/json'
    return json.dumps(products)

run(host='0.0.0.0', port=8083, reloader=True)
