# !/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, json, sqlite3, datetime, urllib
from bottle import get, post, run, request, response
from dateutil import parser, tz

travelCats = {
    "adults":"Vuxen",
    "small-children":"Barn (2–6 år)",
    "children":"Barn (7–15 år)",
    "youths":"Ungdom (16–25 år)",
    "students":"Student",
    "seniors":"Pensionär"
}

stops = {
    "740000001":"b9501164-fbb4-454a-8918-38a042780790",
    "740000002":"b9501164-fbb4-454a-8918-38a042780795",
    "740000008":"b9501164-fbb4-454a-8918-38a042780792",
    "740000055":"b9501164-fbb4-454a-8918-38a042780791",
    "740000018":"b9501164-fbb4-454a-8918-38a042780794",
    "740000040":"b9501164-fbb4-454a-8918-38a042780793",
    "740001579":"b9501164-fbb4-454a-8918-38a042780797",
    "740000110":"b9501164-fbb4-454a-8918-38a042780796",
    "740000080":"b9501164-fbb4-454a-8918-38a042780798",
    "740000765":"32102a6e-4763-49ac-9fd0-2fcdbe587a1a"
}

def TimeStampToIso(tstamp):
  return datetime.datetime.fromtimestamp(tstamp).strftime("%Y-%m-%dT%H:%M:%SZ")

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
  return stops[id]

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

    headers = {
      'content-type': 'application/json',
      'accept': 'application/json, text/plain, */*'
      }
    query = {
        "origin_id":StopIdToName(search["route"][0]["stopId"]),
        "destination_id":StopIdToName(search["route"][1]["stopId"]),
        "date":search["temporal"]["earliestDepature"][0:10],
        "passengers":[1],
        "has_stroller":False,
        "has_pet":False,
        "wheelchairs":0
    }

    result = requests.post(
        "https://api.mtrexpress.travel/api/v1.0/departures/",
        data=json.dumps(query),
        headers=headers
        )

    trips = []
    for trip in result.json():
        if stringToUnixTS(trip["departure_at"]) >= stringToUnixTS(search["temporal"]["earliestDepature"]) and stringToUnixTS(trip["arrival_at"]) <= stringToUnixTS(search["temporal"]["latestArrival"]):
            trips.append(trip)
    
    products = []
    for trip in trips:
      pricelist = []
      url = "https://mtrexpress.travel/sv/boka-resa?from="+trip["origin"]["name"]+"&to="+trip["destination"]["name"]+"&date="+trip["departure_at"][0:10]+"&adults=1&show=departures"
      for type in ["FIX","FLEX","PLUS"]:
        pris = float(trip["prices"][type])
        pricelist.append({
            "productId": url,
            "productTitle": type,
            "productDescription": type + " Biljett",
            "fares": [
                {
                    "amount": pris,
                    "currency": "SEK",
                    "vatAmount": round(pris*0.06,2),
                    "vatPercent": 6
                }
            ],
            "productProperties": {
                "date": trip["departure_at"]
            },
            "travellersPerCategory": search["travellersPerCategory"]
        })
      products.append(pricelist)
    response.content_type = 'application/json'
    return json.dumps(products)

run(host='0.0.0.0', port=8081, reloader=True)