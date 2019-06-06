# !/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, json, sqlite3, datetime, urllib, rt90, time
from bottle import get, post, run, request, response
from dateutil import parser, tz
from ConfigParser import ConfigParser

travelCats = {
    "VU":"Vuxen",
    "BA":"Barn (8-17 år)",
    "UN":"Ungdom (18-25 år)"
}

stops = sqlite3.connect('stops')

def isoToTimeStamp(string):
  try:
    utc_dt = datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.%fZ')
  except:
    utc_dt = datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%SZ')
  return (utc_dt - datetime.datetime(1970, 1, 1)).total_seconds()

def stringToUnixTS(string):
  utc_dt = parser.parse(string).astimezone(tz.tzutc());
  return (utc_dt - datetime.datetime(1970, 1, 1, tzinfo=tz.tzutc())).total_seconds()

@post('/api/v1/buy')
def cats():
    response.content_type = 'application/json'
    returndata = {"payUrl":"https://www.arlandaexpress.se/"}
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
    
    stops = ["740000492","740000708","740000001"]
    if search["route"][0]["stopId"] in stops and search["route"][-1]["stopId"] in stops:
        pass
    else:
        response.content_type = 'application/json'
        return json.dumps([[]])
    
    ttime = stringToUnixTS(search["temporal"]["earliestDepature"])
    products = []
    for trip in [1]:
        pricelist = []
        if search["travellersPerCategory"][0]["cat"] == "VU":
            if (ttime - time.time() > 3600*24*8):
                pris = 195
                url = "fix"
            else:
                pris = 295
                url = "flex"
            vat = pris*0.06
            pricelist.append({
                "productId": url,
                "productTitle": "Enkelbiljett",
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
        else:
            url = "fix"
            pris = 165
            vat = pris*0.06
            pricelist.append({
                "productId": url,
                "productTitle": "Enkelbiljett",
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

run(host='127.0.0.1', port=8092, reloader=True)