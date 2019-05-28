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

def StopIdToData(id):
  for row in stops.execute("SELECT stop_lat,stop_lon,stop_name FROM stops WHERE stop_id = %s" % id):
    lat = row[0]
    lon = row[1]
    name = row[2]
  for row in stops.execute("SELECT agency_stop_id FROM astops WHERE agency_id = 256 AND stop_id = %s" % id):
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
    data = {
        "withinkalmar":"true",
        "travelfrom[Id]":fromdata["id"],
        "travelfrom[Name]":fromdata["name"],
        "travelfrom[PointTypeId]":"0",
        "travelfrom[CustomFields]":"",
        "travelfrom[Coordinate][X]":fromdata["Y"],
        "travelfrom[Coordinate][Y]":fromdata["Y"],
        "travelto[Id]":"302001",
        "travelto[Name]":"Alvesta",
        "travelto[PointTypeId]":"0",
        "travelto[CustomFields]":"",
        "travelto[Coordinate][X]":"56.8989526025308",
        "travelto[Coordinate][Y]":"14.5572810453009",
        "traveldate":"05/27/2019 10:37:30",
        "traveltime":"05/27/2019 10:37:30",
        "shorttraveldate":"2019-05-27",
        "shorttraveltime":"10:37",
        "traveltypelist[0][Disabled]":"false",
        "traveltypelist[0][Group]":"",
        "traveltypelist[0][Selected]":"true",
        "traveltypelist[0][Text]":"Avgång",
        "traveltypelist[0][Value]":"0",
        "traveltypelist[1][Disabled]":"false",
        "traveltypelist[1][Group]":"",
        "traveltypelist[1][Selected]":"false",
        "traveltypelist[1][Text]":"Ankomst",
        "traveltypelist[1][Value]":"1",
        "traveltype":"0",
        "travelfilterlist[0][Id]":"1",
        "travelfilterlist[0][Name]":"Skärgårdstrafik",
        "travelfilterlist[0][DefaultChecked]":"true",
        "travelfilterlist[0][Checked]":"true",
        "travelfilterlist[1][Id]":"2",
        "travelfilterlist[1][Name]":"Närtrafik",
        "travelfilterlist[1][DefaultChecked]":"true",
        "travelfilterlist[1][Checked]":"true",
        "travelfilterlist[2][Id]":"4",
        "travelfilterlist[2][Name]":"Landsbygdsbuss",
        "travelfilterlist[2][DefaultChecked]":"true",
        "travelfilterlist[2][Checked]":"true",
        "travelfilterlist[3][Id]":"8",
        "travelfilterlist[3][Name]":"Stadsbuss",
        "travelfilterlist[3][DefaultChecked]":"true",
        "travelfilterlist[3][Checked]":"true",
        "travelfilterlist[4][Id]":"16",
        "travelfilterlist[4][Name]":"Tåg",
        "travelfilterlist[4][DefaultChecked]":"true",
        "travelfilterlist[4][Checked]":"true"
    }
    headers = {"Content-Type":"application/x-www-form-urlencoded;charset=UTF-8"} 
    result = requests.post(
        "https://www.kalmarlanstrafik.se/api/TravelPlannerApi/GetJourney"   headers = headers,
        data= data,
        headers = headers
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

run(host='0.0.0.0', port=8086, reloader=True)