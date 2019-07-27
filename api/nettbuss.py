# !/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, json, sqlite3, datetime, urllib, math
from nbstops import stops
from bottle import get, post, run, request, response
from dateutil import parser, tz
from urllib import urlencode


travelCats = {
    "ADULT":"Vuxen (26-64 år)",
    "THE_YOUNG":"Ungdom (16-25 år)",
    "THE_ELDERLY":"Senior (65+ år)",
    "STUDENTS":"Student",
    "CHILDREN":"Barn (7-15 år)",
    "BABY":"Barn (0-6 år)"
}

db = sqlite3.connect("../static_data/stops")

def TimeStampToIso(tstamp):
  return datetime.datetime.fromtimestamp(tstamp).strftime("%Y-%m-%dT%H:%M:%SZ")

def isoToDate(string):
  try:
    utc_dt = datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.%fZ')
  except:
    utc_dt = datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%SZ')
  return utc_dt.strftime("%Y-%m-%d")

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
  
def isoToTimeStampNB(string):
  try:
    utc_dt = datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.%fZ')
  except:
    utc_dt = datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%SZ')
  return (utc_dt - datetime.datetime(1970, 1, 1)).total_seconds()-(3600*2)

def stringToUnixTS(string):
  utc_dt = parser.parse(string).astimezone(tz.tzutc());
  return (utc_dt - datetime.datetime(1970, 1, 1, tzinfo=tz.tzutc())).total_seconds()

def StopIdToName(id):
  return stops[id]

@post('/api/v1/buy')
def cats():
    response.content_type = 'application/json'
    returndata = {"payUrl":"https://track.adtraction.com/t/t?a=1213626540&as=1403272214&t=2&tk=1&url="+request.json["productId"]}
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

    query = {
        "StepId":2,
        "OriginBusStopId":StopIdToName(search["route"][0]["stopId"]),
        "DestinationBusStopId":StopIdToName(search["route"][1]["stopId"]),
        "DepartureDate":isoToDate(search["temporal"]["earliestDepature"]),
        "ReturnDate":"0",
        "FareClassSelections":"",
        "TravelPassNumber":None
    }

    headers = {
      'content-type': 'application/json',
      'accept': 'application/json, text/plain, */*'
      }
    
    for traveller in search["travellersPerCategory"]:
        query["FareClassSelections"] += "BONUS_SCHEME_GROUP."+traveller['cat']+","+str(traveller['tra'])+";"

    result = requests.post(
        "https://www.nettbuss.se/sv/api/booking/GetDepartureJourneys",
        data=json.dumps(query),
        headers=headers
        )
    
    trips = []
    jsondata = json.loads(result.json())
    if "LaterJourneys" in jsondata and isinstance(jsondata["LaterJourneys"],(list,)):
        jsondata["VisibleJourneys"].extend(jsondata["LaterJourneys"])
    for trip in jsondata["VisibleJourneys"]:
        if isoToTimeStampNB(trip["PlannedDeparture"]) >= stringToUnixTS(search["temporal"]["earliestDepature"]) and isoToTimeStampNB(trip["PlannedArrival"]) <= stringToUnixTS(search["temporal"]["latestArrival"]):
            trips.append(trip)

    products = []
    for trip in trips:
      pricelist = []
      url = "http://www.nettbuss.se/boka/#!/2/"+query["OriginBusStopId"]+"/"+query["DestinationBusStopId"]+"/"+query["DepartureDate"]+"/0/"+query["FareClassSelections"]+"/";
      for type in trip["Options"]:
        pris = float(type['Price'])
        pricelist.append({
            "productId": url,
            "productTitle": type["Name"],
            "productDescription": ", ".join(type["Benefits"]),
            "fares": [
                {
                    "amount": pris,
                    "currency": "SEK",
                    "vatAmount": round(pris*0.06,2),
                    "vatPercent": 6
                }
            ],
            "productProperties": {
                "date": trip["PlannedDeparture"]
            },
            "travellersPerCategory": search["travellersPerCategory"]
        })
      products.append(pricelist)
    response.content_type = 'application/json'
    return json.dumps(products)

run(host='127.0.0.1', port=8084, reloader=True)
