 # !/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, json, sqlite3, datetime, urllib, math
from bottle import get, post, run, request, response
from dateutil import parser, tz
from urllib import urlencode, quote_plus
from ConfigParser import ConfigParser
import slstops

travelCats = {
    "VU":"Vuxen"
}

def utcIsoToLocalData(datedate):
    data = parser.parse(datedate).astimezone(tz.gettz("Europe/Stockholm")).strftime("%H,%I,%w")
    return map(int, data.split(","))

@post('/api/v1/buy')
def cats():
    response.content_type = 'application/json'
    returndata = {"payUrl":"http://akerbergstrafik.se/trosabussen-kop-biljett/"}
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
    timedata = utcIsoToLocalData(search["temporal"]["earliestDepature"])
    if search["route"][-1]["stopId"] == "740004046" and timedata[0] >= 12 and timedata[2] > 0 and timedata[2] < 6:
      pris=100
    elif search["route"][0]["stopId"] == "740004046" and timedata[0] < 13 and timedata[2] > 0 and timedata[2] < 6:
      pris=100
    else:
      pris = 150
    products = []
    pricelist = []
    pricelist.append({
            "productId": "single",
            "productTitle": "Enkelbiljett",
            "fares": [
                {
                    "amount": pris,
                    "currency": "SEK",
                    "vatAmount": round(pris*0.06,2),
                    "vatPercent": 6
                }
            ],
            "productProperties": {
                "date": search["temporal"]["earliestDepature"]
            },
            "travellersPerCategory": search["travellersPerCategory"]
        })
    pris = 1020
    pricelist.append({
            "productId": "10bilj",
            "productTitle": "10 Biljett",
            "fares": [
                {
                    "amount": pris,
                    "currency": "SEK",
                    "vatAmount": round(pris*0.06,2),
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

run(host='127.0.0.1', port=8106, reloader=True)
