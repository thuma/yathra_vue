# !/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, json, sqlite3, datetime, urllib, rt90, math
from bottle import get, post, run, request, response
from dateutil import parser, tz

travelCats = {
    "VU":"Vuxen",
    "UN1":"Ungdom (7-19 år)",
    "UN2":"Ungdom (20-25 är)"
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
  for row in stops.execute("SELECT stop_lat,stop_lon,stop_name FROM stops WHERE stop_id = %s" % id):
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

    params = {"inpPointfr":row[2]}
    findbn = requests.get(
        "http://www.labs.skanetrafiken.se/v2.2/querystation.asp",
        params = params
        )
    points = GetFirstValue(findbn.content,"StartPoints")
    point = GetFirstValue(points,"Point")
    nid = GetFirstValue(point,"Id")
    X = int(GetFirstValue(point,"X"))
    Y = int(GetFirstValue(point,"Y"))
    dist =  math.sqrt(abs(X - coords[0])**2+abs(Y - coords[1])**2)
    if dist > 250:
      return find.content.split("NearestStopArea><Id>")[1].split("</Id>")[0]
    else:
      return nid

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
        "inpPointFr_ajax":"Mora resecentrum (Mora)|562152|0",
        "inpPointTo_ajax":"Orsa busstn (Orsa)|534063|0",
        "inpPointInterm_ajax":"",
        "inpPointFr":"Mora resecentrum (Mora)",
        "inpPointTo":"Orsa busstn (Orsa)",
        "selDirection":"0",
        "inpTime":"07:46",
        "inpDate":"2019-06-19",
        "x":"11",
        "y":"7",
        "selPriceType":"0",
        "cmdAction":"search",
        "EU_Spirit":"False",
        "TNSource":"",
        "SupportsScript":"True",
        "Language":"se",
        "VerNo":"",
        "selRegionFr":"741",
        "optTypeFr":"0",
        "optTypeTo":"0",
        "inpWaitTime":"",
        "selChangeTime":"0",
        "selPriority":"0",
        "selWalkSpeed":"0",
        "optReturn":"0",
        "selPointFr":"Mora resecentrum (Mora)|562152|0",
        "selPointTo":"Orsa busstn (Orsa)|534063|0",
        "selPointFrKey":"562152",
        "selPointToKey":"534063",
        "selPointInterm":"",
        "selPointIntermKey":"",
        "TrafficMask":"",
        "RSH":"",
        "FirstStart":"2019-06-19 07:45:00",
        "LastStart":"2019-06-19 09:45:00",
        "FirstStart2":"",
        "LastStart2":"",
        "CacheFile":"1145284971809147253",
        "CacheFile2":"",
        "CacheFileSingleStation":"",
        "inpDate2":"2019-06-19",
        "inpTime2":"11:48",
        "selDirection2":"0",
        "selSingleStation":"",
        "selSingleStationKey":"",
        "selComboJourney":"0",
        "chkWalkToOtherStop":"0",
        "inpDateSingleStation":"2019-06-19",
        "inpTimeSingleStation":"07:48",
        "selDirectionSingleStation":"0",
        "Source":"resultspage",
        "HtmlSource":"",
        "inpSender":""
    }

    result = requests.get(
        "https://reseplanerare.fskab.se/dalarna/v2/resultspage.asp",
        data = data
        )
    trips = [1]
   
    products = []

    for trip in trips:
        pricelist = []
        prices = result.content.split("priceArr[0]")[1].split("(")[1].split(")")[0].split(",")
        for i, price in prices:
            pris = float(price)
            vat = round(pris*0.06,2)
            url = "https://www.dalatrafik.se/sv/biljetter/"
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
                    "date": "--::"
                },
                "travellersPerCategory": search["travellersPerCategory"]
            })
        products.append(pricelist)
    response.content_type = 'application/json'
    return json.dumps(products)

run(host='127.0.0.1', port=8095, reloader=True)