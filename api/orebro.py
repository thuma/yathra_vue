# !/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, json, sqlite3, datetime, urllib, rt90, math, re
from bottle import get, post, run, request, response
from dateutil import parser, tz

travelCats = {
    "VU":"Vuxen (20- år)",
    "BA":"Barn (0-6 år)",
    "UN":"Ungdom (7–19 år)",
    "FA":"Familj (5 personer max 2 vuxna)"
}

stops = sqlite3.connect('../static_data/stops')

def TimeStampToIso(tstamp):
  return datetime.datetime.fromtimestamp(tstamp).strftime("%Y-%m-%dT%H:%M:%SZ")
  
def utcIsoToLocalSktrDate(datedate):
   return (parser.parse(datedate).astimezone(tz.gettz("Europe/Stockholm"))-datetime.timedelta(minutes=10)).strftime("%Y-%m-%d")
 
def utcIsoToLocalSktrTime(datedate):
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

def StopIdToName(id):
  for row in stops.execute("SELECT agency_stop_id FROM astops WHERE stop_id = %s and agency_id = 289" % id):
    return str(row[0])

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
    
    data = {
        "from":StopIdToName(search["route"][0]["stopId"]),
        "fromType":"0",
        "to":StopIdToName(search["route"][-1]["stopId"]),
        "toType":"0",
        "when":utcIsoToLocalSktrTime(search["temporal"]["earliestDepature"])+" "+utcIsoToLocalSktrDate(search["temporal"]["earliestDepature"]),
        "direction":"0",
        "changeTime":"NORMAL",
        "priority":"SHORTEST_TIME",
        "walkDistance":"0",
        "selectedMeansOfTransport":"1,2",
        "span":"2"
    }

    result = requests.get(
        "https://www.lanstrafiken.se/sv/render/TravelPlannerAPIRenderer/GetJourneys/",
        params = data
        )
    trips = [1]
    products = []
    prices = result.content.split('<caption class="f-s:h5 m-b:0 show-for-sr">Priser</caption>')[1].split("<tbody>")[1].split("</tbody>")[0].split("<tr>")[1:]
    pdata = []
    travelCatsNames = {
        "VU":"vuxen",
        "BA":"barn",
        "UN":"skolungdom",
        "FA":"familj"
    }

    for price in prices:
      parts = price.split("<td>")
      if travelCatsNames[search["travellersPerCategory"][0]["cat"]] in parts[1]:
        pdata.append({"name":parts[1].split("<")[0].strip().replace("&#246;","ö"),"price":float(parts[2].strip().split("k")[0].replace(",","."))})

    for trip in trips:
        pricelist = []
        for price in pdata:
            pris = price["price"]
            vat = round(pris*0.06,2)
            url = "https://www.lanstrafiken.se/biljett-och-kop/"

            pricelist.append({
                "productId": url,
                "productTitle": price["name"],
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
        pricelist.sort(key=lambda x: x["fares"][0]["amount"], reverse=False)
        products.append(pricelist)
    response.content_type = 'application/json'
    return json.dumps(products)

run(host='127.0.0.1', port=8098, reloader=True)