# !/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, json, sqlite3, datetime, urllib, math
from bottle import get, post, run, request, response
from dateutil import parser, tz
from urllib import urlencode, quote_plus

travelCats = {
    "VU":"Vuxen",
    "RB":"Rabatterat"
}

stops = sqlite3.connect('stops')

def getLocationPos(id):
  for row in stops.execute("SELECT stop_lat,stop_lon FROM stops WHERE stop_id = %s" % id):
    lat = row[0]
    lon = row[1]
  return {"lat":lat, "lon":lon}

@post('/api/v1/buy')
def cats():
    response.content_type = 'application/json'
    returndata = {"payUrl":"https://sl.se/sv/kop-biljett/"}
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
    opos = getLocationPos(search["route"][0]["stopId"])
    dpos = getLocationPos(search["route"][-1]["stopId"])
    
    
    search["temporal"]["earliestDepature"]
    

    
    parameters = {
        "date":"2019-06-10",
        "time":"12:00",
        "originCoordLat":opos['lat'],
        "originCoordLong":opos['lon'],
        "destCoordLat":dpos['lat'],
        "destCoordLong":dpos['lon'],
        "key":"",
        "lang":"se"
    }
    result = requests.get("https://api.sl.se/api2/TravelplannerV3_1/trip.json?"+urlencode(parameters))
    print result.json()

    products = []
    for trip in ["one"]:
      pricelist = []
      for type in ["one"]:
        pricelist.append({
            "productId": "id1",
            "productTitle": "Biljett",
            "productDescription": "Reskassa Vuxen enkel",
            "fares": [
                {
                    "amount": 32,
                    "currency": "SEK",
                    "vatAmount": round(32*0.06,2),
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

run(host='127.0.0.1', port=8088, reloader=True)
