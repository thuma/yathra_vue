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
  
def utcIsoToLocalULDateTime(datedate):
   return (parser.parse(datedate).astimezone(tz.gettz("Europe/Stockholm"))-datetime.timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")
 
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
  for row in stops.execute("SELECT agency_stop_id FROM astops WHERE agency_id = 251 AND stop_id = %s" % id):
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
    "changeTimeType":"0",
    "dateTime":utcIsoToLocalULDateTime(search["temporal"]["earliestDepature"]),
    "from":fromdata["name"],
    "fromPointId":fromdata["id"],
    "fromPointType":"0",
    "maxWalkDistance":"3000",
    "priorityType":"0",
    "to":todata["name"],
    "toPointId":todata["id"],
    "toPointType":"0",
    "trafficTypes":"1,2,3,4,5,6,7,8,9,10,11",
    "travelWhenType":"0",
    "via":"",
    "viaPointId":"",
    "walkSpeedType":"0"
    }

    result = requests.get(
        "https://www.ul.se/api/journey/search",
        params=params
        )
    trips = []

    for trip in json.loads(result.json()["Payload"]):
        if stringToUnixTS(trip["departureDateTime"]+"+02:00") >= stringToUnixTS(search["temporal"]["earliestDepature"]) and stringToUnixTS(trip["arrivalDateTime"]+"+02:00") <= stringToUnixTS(search["temporal"]["latestArrival"]):
            trips.append(trip)
   
    products = []
    find = {
        "VU":"Reskassa Vuxen",
        "UN":"Reskassa Ungdom",
        }

    findindex = {
        "VU":0,
        "UN":1,
        }
 
    for trip in trips:
        pricelist = []
        url = "https://www.ul.se/biljetter/reskassa/vuxen/"
        pris = trip["ticketType"]["priceClasses"][findindex[search["travellersPerCategory"][0]["cat"]]]["prices"][1]["value"]/100
        vat =  pris*0.06
        
        pricelist.append({
            "productId": url,
            "productTitle": "Enkelbiljett",
            "productDescription": "Reskassa Vuxen" ,
            "fares": [
                {
                    "amount": pris,
                    "currency": "SEK",
                    "vatAmount": vat,
                    "vatPercent": 6
                }
            ],
            "productProperties": {
                "date": trip["departureDateTime"]
            },
            "travellersPerCategory": search["travellersPerCategory"]
        })
        products.append(pricelist)
    response.content_type = 'application/json'
    return json.dumps(products)

run(host='127.0.0.1', port=8090, reloader=True)