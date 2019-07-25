# !/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, json, sqlite3, datetime, urllib, rt90
from bottle import get, post, run, request, response
from dateutil import parser, tz

travelCats = {
    "VU":"Vuxen",
    "BA":"Barn",
    "DU":"Familj"
}

stops = sqlite3.connect('../static_data/stops')

def TimeStampToIso(tstamp):
  return datetime.datetime.fromtimestamp(tstamp).strftime("%Y-%m-%dT%H:%M:%SZ")
  
def utcIsoToLocalOtrDate(datedate):
   return (parser.parse(datedate).astimezone(tz.gettz("Europe/Stockholm"))-datetime.timedelta(minutes=10)).strftime("%Y-%m-%d")
 
def utcIsoToLocalOtrTime(datedate):
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
  for row in stops.execute("SELECT agency_stop_id FROM astops WHERE agency_id = 253 AND stop_id = %s" % id):
    id = row[0]
  return {"name":name, "id":id, "X":lat, "Y":lon}
   
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
    
    params = {
        "startId":fromdata["id"],
        "endId":todata["id"],
        "startType":"stop",
        "endType":"stop",
        "startLl":str(fromdata["X"])+","+str(fromdata["Y"]),
        "endLl":str(todata["X"])+","+str(todata["Y"]),
        "startName":fromdata["name"],
        "endName":todata["name"],
        "date":utcIsoToLocalOtrDate(search["temporal"]["earliestDepature"]),
        "time":utcIsoToLocalOtrTime(search["temporal"]["earliestDepature"]),
        "direction":"0",
        "span":"default",
        "traffictypes":"0",
        "changetime":"0",
        "priority":"0",
        "walk":"false"
        }

    result = requests.get(
        "https://rest.ostgotatrafiken.se/journey/Find",
        params=params
        )
    
    trips = []
    for trip in result.json()["Journeys"]:
        if stringToUnixTS(trip["Departure"]+"+02:00") >= stringToUnixTS(search["temporal"]["earliestDepature"]) and stringToUnixTS(trip["Arrival"]+"+02:00") <= stringToUnixTS(search["temporal"]["latestArrival"]):
            trips.append(trip)
   
    products = []
    find = {
        "VU":"Reskassa Vuxen",
        "BA":"Reskassa Barn",
        "DU":"Reskassa Duo/Familj"
        }

    findindex = {
        "VU":3,
        "BA":4,
        "DU":5
        }
 
    for trip in trips:
        pricelist = []
        url = "https://www.ostgotatrafiken.se/biljetter/biljettertyper/enkelbiljett/"
        pris = trip["Prices"][findindex[search["travellersPerCategory"][0]["cat"]]]["Price"]
        vat =  trip["Prices"][findindex[search["travellersPerCategory"][0]["cat"]]]["Price"]
        
        pricelist.append({
            "productId": url,
            "productTitle": "Enkelbiljett",
            "productDescription": trip["Prices"][findindex[search["travellersPerCategory"][0]["cat"]]]["PriceType"] ,
            "fares": [
                {
                    "amount": pris,
                    "currency": "SEK",
                    "vatAmount": vat,
                    "vatPercent": 6
                }
            ],
            "productProperties": {
                "date": trip["Departure"]
            },
            "travellersPerCategory": search["travellersPerCategory"]
        })
        products.append(pricelist)
    response.content_type = 'application/json'
    return json.dumps(products)

run(host='127.0.0.1', port=8089, reloader=True)