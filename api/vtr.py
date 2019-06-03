# !/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, json, sqlite3, datetime, urllib, rt90
from bottle import get, post, run, request, response
from dateutil import parser, tz

travelCats = {
    "VU":"Vuxen",
    "UN":"Ungdom (7-19 år)"
}


stops = sqlite3.connect('stops')

def TimeStampToIso(tstamp):
  return datetime.datetime.fromtimestamp(tstamp).strftime("%Y-%m-%dT%H:%M:%SZ")
  
def utcIsoToLocalVtrDate(datedate):
   return (parser.parse(datedate).astimezone(tz.gettz("Europe/Stockholm"))-datetime.timedelta(minutes=10)).strftime("%Y-%m-%d")
 
def utcIsoToLocalVtrTime(datedate):
   return (parser.parse(datedate).astimezone(tz.gettz("Europe/Stockholm"))-datetime.timedelta(minutes=10)).strftime("%H:%M")

def GetFirstValue(data, field):
    try:
        return data.split("<"+field+">")[1].split("</"+field+">")[0]
    except:
        return ""

def isoToTimeStamp(string):
  try:
    utc_dt = datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.%fZ')
  except:
    utc_dt = datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%SZ')
  return (utc_dt - datetime.datetime(1970, 1, 1)).total_seconds()

def stringToUnixTS(string):
  utc_dt = parser.parse(string).astimezone(tz.tzutc());
  return (utc_dt - datetime.datetime(1970, 1, 1, tzinfo=tz.tzutc())).total_seconds()

def StopIdToData(id):
  for row in stops.execute("SELECT stop_lat,stop_lon,stop_name FROM stops WHERE stop_id = %s" % id):
    lat = row[0]
    lon = row[1]
    name = row[2]
  return {"name":name, "lat":lat, "lon":lon}
 
@post('/api/v1/buy')
def cats():
    response.content_type = 'application/json'
    returndata = {"payUrl":request.json["productId"]}
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
    fromdata = StopIdToData(search["route"][0]["stopId"])
    todata = StopIdToData(search["route"][-1]["stopId"])
    
    headers = {"Authorization": "Bearer 1c806ebc-d119-3aca-8061-77210481408e"}
    params = {
        "originCoordLat":fromdata["lat"],
        "originCoordLong":fromdata["lon"],
        "originCoordName":fromdata["name"],
        "destCoordLat":todata["lat"],
        "destCoordLong":todata["lon"],
        "destCoordName":todata["name"],
        "date":utcIsoToLocalVtrDate(search["temporal"]["earliestDepature"]),
        "time":utcIsoToLocalVtrTime(search["temporal"]["earliestDepature"]),
        "format":"json"
    }
    location = requests.get("https://api.vasttrafik.se/bin/rest.exe/v2/trip", params=params, headers=headers)
    print location.json()
    data = location.json()["TripList"]["Trip"][0]["Leg"]
    headers = {
        "atok1":"HfMhQQbm8PBL182tYwrDFWfQDpelbAzBX9EkBBzZgt2IbUQNkPw31BHSfpAe9MRzWUeQew421jaDEtOiP1hlPfiniKVIjJWtdHXtKqDop4I1",
        "atok2":"9eY5tb5uxJ2OMg1bQ0qPuEJx12EDNMHvwQ-r8OWy2VX8skm2oHywE99-hWj-J_1GCiICN7tN7Sy_aaXJ05k8nmg1JAi8elxtOWhuUx8YdtI1"}
    result = requests.post('https://www.vasttrafik.se/api/travelplanner/v2/price', headers=headers, json={"leg":data})
  
    products = []
    print result.json()
    for trip in result.json():
        pricelist = []
        url = "https://www.vasttrafik.se/biljetter/enkelbiljetter/"
        pris = float(trip['price'])
        vat = pris*0.06
        pricelist.append({
            "productId": url,
            "productTitle": "Enkelbiljett APP",
            "productDescription": "Bokas i appen",
            "fares": [
                {
                    "amount": pris,
                    "currency": "SEK",
                    "vatAmount": vat,
                    "vatPercent": 6
                }
            ],
            "productProperties": {
                "date": search["temporal"]["earliestDepature"]
            },
            "travellersPerCategory": search["travellersPerCategory"]
        })
        products.append(pricelist)
        response.content_type = 'application/json'
        return json.dumps(products)

run(host='127.0.0.1', port=8091, reloader=True)