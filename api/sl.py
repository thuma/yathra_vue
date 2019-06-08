# !/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, json, sqlite3, datetime, urllib, math
from bottle import get, post, run, request, response
from dateutil import parser, tz
from urllib import urlencode, quote_plus
from ConfigParser import ConfigParser
import slstops

travelCats = {
    "VU":"Vuxen",
    "RB":"Rabatterat"
}

config = ConfigParser()
config.read('../../settings.ini')

stops = sqlite3.connect('../static_data/stops')

def getLocationPos(id):
  for row in stops.execute("SELECT stop_lat,stop_lon,stop_name FROM stops WHERE stop_id = %s" % id):
    lat = row[0]
    lon = row[1]
    name = row[2]
  for row in stops.execute("SELECT * FROM astops WHERE agency_id = 275 AND stop_id = %s" % id):
    exid =  row[2]
  exid = slstops.getByArea(exid)
  if id == "740001617":
    exid = "1080"
  return {"name":name, "lat":lat, "lon":lon, "id":exid}

def utcIsoToLocalSlDate(datedate):
   return (parser.parse(datedate).astimezone(tz.gettz("Europe/Stockholm"))-datetime.timedelta(minutes=10)).strftime("%Y-%m-%d")
 
def utcIsoToLocalSlTime(datedate):
   return (parser.parse(datedate).astimezone(tz.gettz("Europe/Stockholm"))-datetime.timedelta(minutes=10)).strftime("%H:%M")

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
    
    parameters = {
        "date":utcIsoToLocalSlDate(search["temporal"]["earliestDepature"]),
        "time":utcIsoToLocalSlTime(search["temporal"]["earliestDepature"]),
        "originId":opos['id'],
        #"originCoordLat":opos['lat'],
        #"originCoordLong":opos['lon'],
        "destId":dpos['id'],
        #"destCoordLat":dpos['lat'],
        #"destCoordLong":dpos['lon'],
        "key":config.get("sl","key"),
        "lang":"se"
    }
    result = requests.get("https://api.sl.se/api2/TravelplannerV3_1/trip.json?"+urlencode(parameters))
    
    products = []
    for trip in ["one"]:
      pricelist = []
      for type in [0,1]:
        name = ["Reskassa", "Butik"]
        
        if result.json()["Trip"][0]["TariffResult"]["fareSetItem"][0]["fareItem"][0]["name"] == 'MESSAGE':
            if result.json()["Trip"][0]["TariffResult"]["fareSetItem"][0]["fareItem"][0]["desc"] == 'TEXT_RULE03':
                pris = 15200
                url = "https://sl.se/sv/kop-biljett/"
            elif result.json()["Trip"][0]["TariffResult"]["fareSetItem"][0]["fareItem"][0]["desc"] == 'TEXT_RULE10':
                if "740000559" in [search["route"][0]["stopId"],search["route"][-1]["stopId"]] and "740000005" not in [search["route"][0]["stopId"],search["route"][-1]["stopId"]]:
                     pris = 6400
                     url = "https://www.ul.se/biljetter/reskassa/vuxen/"
                if "740000559" in [search["route"][0]["stopId"],search["route"][-1]["stopId"]] and "740000005" in [search["route"][0]["stopId"],search["route"][-1]["stopId"]]:
                     pris = 5000
                     url = "https://www.ul.se/biljetter/reskassa/vuxen/"
                else:
                     pris = 9600
                url = "https://sl.se/sv/kop-biljett/"
            else:
                print result.json()["Trip"][0]["TariffResult"]["fareSetItem"][0]["fareItem"][0]["desc"]
                pris = 9600
                url = "https://sl.se/sv/kop-biljett/"
        else:
            pris  = result.json()["Trip"][0]["TariffResult"]["fareSetItem"][0]["fareItem"][type]["price"]
            url = "https://sl.se/sv/kop-biljett/"
        pricelist.append({
            "productId": url,
            "productTitle": name[type] + " Vuxen",
            "fares": [
                {
                    "amount": pris/100,
                    "currency": "SEK",
                    "vatAmount": round(pris/100*0.06,2),
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
