# !/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, json, sqlite3, datetime, urllib, dateutil
from bottle import get, post, run, request, response
from dateutil import parser, tz

travelCats = {
  "VU":"Vuxen",
  "BO":"Barn/Ungdom",
  "SU":"Student",
  "SE":"Senior"
}

def TimeStampToIso(tstamp):
  return datetime.datetime.fromtimestamp(tstamp).strftime("%Y-%m-%dT%H:%M:%SZ")

def isoToTimeStamp(string):
  try:
    utc_dt = datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.%fZ')
  except:
    utc_dt = datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%SZ')
  return (utc_dt - datetime.datetime(1970, 1, 1)).total_seconds()

def StopIdToName(id):
  if id in stopids:
    return stopids[id].decode("utf-8")
  for row in stops.execute("SELECT stop_name FROM stops WHERE stop_id = %s" % id):
   return row[0]

def stringToUnixTS(string):
  utc_dt = parser.parse(string).astimezone(tz.tzutc());
  return (utc_dt - datetime.datetime(1970, 1, 1, tzinfo=tz.tzutc())).total_seconds()

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
 
    travelers = []
    for traveler in search["travellersPerCategory"]:
      for a in range(traveler["tra"]):
        travelers.append({
          "travellerCategory":traveler["cat"]
        })
   
    query = {
        "departureLocationId":int(search["route"][0]["stopId"][2:]),
        "departureLocationProducerCode":int(search["route"][0]["stopId"][0:2]),
        "arrivalLocationId":int(search["route"][1]["stopId"][2:]),
        "arrivalLocationProducerCode":int(search["route"][1]["stopId"][0:2]),
        "departureDateTime":search["temporal"]["earliestDepature"][0:10]+" 00:00",
        "travelType":"T",
        "promotionCode":"null",
        "passengers":travelers
    }
    
    print query;
      
    headers = {
      'Content-type': 'application/json;charset=UTF-8',
      'Accept': 'application/json, text/plain, */*',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
           }
  
    tokendata = requests.get("https://www.snalltaget.se/",headers=headers)
    headers['Authorization'] = "Bearer "+tokendata.content.split("window.Bokning.ApiToken")[1].split("'")[1]
    
    result = requests.post(
        "https://www.snalltaget.se/api/timetables",
        data=json.dumps(query).replace('"null"',"null"),
        headers=headers,
        )
    trips = []
    refs = []
    for j in result.json()["journeyAdvices"]:
      if stringToUnixTS(j["departureDateTime"]) >= isoToTimeStamp(search["temporal"]["earliestDepature"]):
        if stringToUnixTS(j["arrivalDateTime"]) <= isoToTimeStamp(search["temporal"]["latestArrival"]):
          trips.append(j)
          refs.append(j["journeyConnectionReference"])

    print trips

    price = {
        "timetableId":result.json()["id"],
        "journeyConnectionReferences":refs
    }
    
    print json.dumps(price)
 
    result = requests.post(
        "https://www.snalltaget.se/api/journeyadvices/lowestprices",
        data=json.dumps(price),
        headers=headers,
        )

    params = {
        "from": query["departureLocationId"],
        "to": query["arrivalLocationId"],
        "t": "T",
        "date": search["temporal"]["earliestDepature"][0:10]+"T00:00:00", 
        "rdate": search["temporal"]["earliestDepature"][0:10]+"T00:00:00",
        "rt": "VU",
        "ra": -1
    }
    print result.content
    products = []	
    for p in result.json():
      pricelist = []
      pris = float(p["lowestTotalPrice"])
      pricelist.append({
            "productId": "specialID",
            "productTitle": "Lägsta pris",
            "productDescription": "Lägsta mjliga pris",
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

run(host='0.0.0.0', port=8085, reloader=True)

