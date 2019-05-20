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

stops = sqlite3.connect('stops')

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
  for row in stops.execute("SELECT stop_lat,stop_lon FROM stops WHERE stop_id = %s" % id):
    coords = rt90.geodetic_to_grid(row[0],row[1])
    params = {
            "x":str(coords[0]).split(".")[0],
            "y":str(coords[1]).split(".")[0],
            "Radius":"500"
            }
    find = requests.get(
        "http://www.labs.skanetrafiken.se/v2.2/neareststation.asp",
        params = params
        )
    return find.content.split("NearestStopArea><Id>")[1].split("</Id>")[0]
    
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
    
    parms = {
            "cmdaction":"search",
            "selPointFr":"A|"+StopIdToName(search["route"][0]["stopId"])+"|0",
            "selPointTo":"B|"+StopIdToName(search["route"][1]["stopId"])+"|0",
            "inpTime":utcIsoToLocalSktrTime(search["temporal"]["earliestDepature"]),
            "inpDate":utcIsoToLocalSktrDate(search["temporal"]["earliestDepature"])
            }
    print "http://www.labs.skanetrafiken.se/v2.2/resultspage.asp?"+ urllib.urlencode(parms)
    result = requests.get(
        "http://www.labs.skanetrafiken.se/v2.2/resultspage.asp",
        params= parms
        )
    trips = []
    for trip in result.content.split("<Journey>"):
        if GetFirstValue(trip,"DepDateTime") <> "" and stringToUnixTS(GetFirstValue(trip,"DepDateTime")+"+02:00")+600 >= stringToUnixTS(search["temporal"]["earliestDepature"]) and stringToUnixTS(GetFirstValue(trip,"ArrDateTime")+"+02:00") <= stringToUnixTS(search["temporal"]["latestArrival"])+600:
            trips.append(trip)
   
    products = []
    find = {
        "VU":"Jojo Reskassa Vuxen",
        "BA":"Jojo Reskassa Barn",
        "DU":"Jojo Reskassa Duo/Familj"
        }
    for trip in trips:
        pricelist = []
        start = GetFirstValue(trip,"DepDateTime")
        url = "https://www.skanetrafiken.se/om-oss/ladda-ner-appen/"
        prisd = trip.split(find[search["travellersPerCategory"][0]["cat"]])[1]
        pris = float(GetFirstValue(prisd,"Price"))
        vat = float(GetFirstValue(prisd,"VAT"))
        pricelist.append({
            "productId": url,
            "productTitle": "Enkelbiljett",
            "productDescription": find[search["travellersPerCategory"][0]["cat"]],
            "fares": [
                {
                    "amount": pris,
                    "currency": "SEK",
                    "vatAmount": vat,
                    "vatPercent": 6
                }
            ],
            "productProperties": {
                "date": start
            },
            "travellersPerCategory": search["travellersPerCategory"]
        })
        products.append(pricelist)
    response.content_type = 'application/json'
    return json.dumps(products)

run(host='0.0.0.0', port=8082, reloader=True)