# !/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, json, sqlite3, datetime, urllib, rt90
from bottle import get, post, run, request, response
from dateutil import parser, tz
from ConfigParser import ConfigParser

travelCats = {
    "VU":"Vuxen",
    "UN":"Ungdom (7-19 år)"
}

config = ConfigParser()
config.read('../../settings.ini')

stops = sqlite3.connect('stops')

def TimeStampToIso(tstamp):
  return datetime.datetime.fromtimestamp(tstamp).strftime("%Y-%m-%dT%H:%M:%SZ")
  
def utcIsoToLocalVtrDate(datedate):
   return (parser.parse(datedate).astimezone(tz.gettz("Europe/Stockholm"))-datetime.timedelta(minutes=10)).strftime("%Y-%m-%d")
 
def utcIsoToLocalVtrTime(datedate):
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

def StopIdToData(id):
  exid = ""
  for row in stops.execute("SELECT stop_lat,stop_lon,stop_name FROM stops WHERE stop_id = %s" % id):
    lat = row[0]
    lon = row[1]
    name = row[2]
  for row in stops.execute("SELECT * FROM astops WHERE agency_id = 279 AND stop_id = %s" % id):
    exid =  row[2]

  vtid = 9021014000000000
  exid = int(exid)*1000
  vtid += exid
  return {"name":name, "lat":lat, "lon":lon, "id":vtid}
 
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
    
    auth = ( config.get("vasttrafik","key"), config.get("vasttrafik","secret"))
    code = requests.post("https://api.vasttrafik.se:443/token", auth = auth, data={"grant_type":"client_credentials","scope":"pris"})

    headers = {"Authorization": "Bearer " + code.json()["access_token"]}
    params = {
        "originId":fromdata["id"],
        "originCoordLat":fromdata["lat"],
        "originCoordLong":fromdata["lon"],
        "originCoordName":fromdata["name"],
        "destId":todata["id"],
        "destCoordLat":todata["lat"],
        "destCoordLong":todata["lon"],
        "destCoordName":todata["name"],
        "date":utcIsoToLocalVtrDate(search["temporal"]["earliestDepature"]),
        "time":utcIsoToLocalVtrTime(search["temporal"]["earliestDepature"]),
        "format":"json"
    }
    location = requests.get("https://api.vasttrafik.se/bin/rest.exe/v2/trip", params=params, headers=headers)
    data = location.json()["TripList"]["Trip"][0]["Leg"]
    if not isinstance(data, (list,)):
      data = [data]
    headers = {
        "atok1":"CvbNODKjS890aMbOWc3mWPB1moL73D25DzCczI57dQsViGWPgPuRzWHWBIU1cWoaOkYRMS6U0ymwAE6nFLgFLPoW9CeAZ4LK-gHI5OftaOY1",
        "atok2":"FaThPf2Mbt9vphriIwZ-EizUpErMw687i6ellV56BTGUbXnl9LUEMdWk4gTvTQaMXx41P6aFC84cCxRdBFB2rG8e-BzrLYXM4LtN2eXmN9w1"}
    result = requests.post('https://www.vasttrafik.se/api/travelplanner/v2/price', headers=headers, json={"leg":data})
  
    print result.content
    products = []
    for trip in result.json():
        pricelist = []
        url = "https://www.vasttrafik.se/biljetter/enkelbiljetter/"
        pris = float(trip['price'])
        vat = pris*0.06
        pricelist.append({
            "productId": url,
            "productTitle": trip["name"],
            "productDescription": "Köps av västtrafik",
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
        if search["travellersPerCategory"][0]["cat"] == "VU" and "Vuxen" in trip["name"]:
            products.append(pricelist)
        elif search["travellersPerCategory"][0]["cat"] == "UN" and "Ungdom" in trip["name"]:
            products.append(pricelist)
    response.content_type = 'application/json'
    return json.dumps(products)

run(host='127.0.0.1', port=8091, reloader=True)