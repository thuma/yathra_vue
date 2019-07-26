# !/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, json, sqlite3, datetime, urllib, rt90, math, re
from bottle import get, post, run, request, response
from dateutil import parser, tz
from geopy.distance import geodesic

travelCats = {
    "VU":"Vuxen",
    "BA":"Barn 7-19 år",
    "UN":"Ungdom 20-35 år",
    "SE":"Senior 65+ år"
}

stops = sqlite3.connect('../static_data/stops')

lpriser = [
[0,7,27,20,14,20,15,9,605,510,510,375,520,445,445,335],
[8,15,36,27,19,29,22,15,750,570,570,375,665,500,500,335],
[16,22,45,33,23,37,28,19,905,695,695,460,790,595,595,395],
[23,30,57,43,28,44,33,22,1040,790,790,520,905,685,685,460],
[31,37,64,48,32,51,38,26,1185,905,905,595,1040,780,780,520],
[38,45,72,54,35,58,44,29,1330,915,1000,665,1165,800,875,580],
[46,52,79,59,40,62,47,31,1475,915,1100,740,1300,800,980,645],
[53,60,88,67,45,72,54,35,1550,915,1165,780,1360,800,1020,675],
[61,67,99,74,49,78,58,40,1620,915,1215,810,1415,800,1060,705],
[68,75,110,83,55,86,66,44],
[76,82,119,89,59,95,71,47],
[83,90,127,95,63,100,75,50],
[91,97,136,102,68,107,80,53],
[98,105,145,108,73,116,87,58],
[106,112,155,116,78,123,93,61],
[113,120,165,124,82,132,99,66],
[121,127,175,131,87,138,104,69],
[128,135,185,139,93,146,109,73],
[136,142,193,146,97,155,116,78],
[143,150,204,153,102,162,122,81],
[151,157,211,158,105,167,125,83],
[158,165,217,163,109,174,130,86],
[166,172,225,168,112,180,135,90],
[173,180,232,175,116,185,139,93],
[181,187,242,182,121,190,142,96],
[188,195,253,189,127,201,150,100],
[196,202,261,196,131,206,154,103],
[203,210,271,203,135,215,161,107],
[211,230,281,210,140,219,164,110],
[231,291,218,146,226,170,113]
]
lprisnamn = [
    "min",
    "max",
    "Vuxen Enkelbiljett",
    "Ungdom/Senior Enkelbiljett",
    "Barn Enkelbiljett",
    "Vuxen 6-Resor",
    "Ungdom/Senior 6-Resor",
    "Barn 6-Resor",
    "Vuxen Periodkort",
    "Senior Periodkort",
    "Ungdom Periodkort",
    "Barn Årskort",
    "Vuxen Årskort",
    "Senior Årskort",
    "Ungdom Årskort",
    "Barn Årskort",
    "",
    "",
    ""
    ]

nrrpriser = [
[0,7,25,21,19,16,19,16,13,11,742,557,557,371],
[8,15,31,26,23,20,23,20,16,14,826,620,620,413],
[16,22,42,36,32,27,32,27,21,18,857,643,643,429],
[23,30,48,41,36,31,36,31,24,20,930,698,698,465],
[31,37,57,48,43,37,43,37,29,25,1097,823,823,549],
[38,45,67,57,50,43,50,43,34,29,1202,902,902,601],
[46,52,75,64,56,48,56,48,38,32,1327,995,995,664],
[53,60,82,70,62,53,62,53,41,35,1421,1066,1066,711],
[61,67,90,77,68,58,68,58,45,38,1526,1145,1145,763],
[68,75,100,85,75,64,75,64,50,43,1609,1207,1207,805],
[76,82,110,94,83,71,83,71,55,47,1724,1293,1293,862],
[83,90,118,100,89,76,89,76,59,50,1745,1309,1309,873],
[91,97,123,105,92,78,92,78,62,53,1756,1317,1317,878],
[98,105,131,111,98,83,98,83,66,56,1766,1325,1325,883],
[106,112,141,120,106,90,106,90,71,60,1777,1333,1333,889],
[113,120,146,124,110,94,110,94,73,62,1797,1348,1348,899],
[121,127,159,135,119,101,119,101,80,68,1818,1364,1364,909],
[128,135,166,141,125,106,125,106,83,71,1891,1418,1418,946],
[136,143,169,144,127,108,127,108,85,72,1975,1481,1481,988],
[144,151,185,157,139,118,139,118,93,79,2059,1544,1544,1030],
[152,157,190,162,143,122,143,122,95,81,2121,1591,1591,1061],
[158,167,204,173,153,130,153,130,102,87,2205,1654,1654,1103],
[168,175,209,178,157,133,157,133,105,89,2320,1740,1740,1160],
[176,181,218,185,164,139,164,139,109,93,2404,1803,1803,1202],
[182,187,230,196,173,147,173,147,115,98,2508,1881,1881,1254],
[188,195,238,202,179,152,179,152,119,101,2654,1991,1991,1327],
[196,201,245,208,184,156,184,156,123,105,2769,2077,2077,1385],
[202,229,271,230,203,173,203,173,136,116,2916,2187,2187,1458],
[230,249,282,240,212,180,212,180,141,120,2936,2202,2202,1468],
[250,267,304,258,228,194,228,194,152,129,3,062,2297,2297,1531],
[268,291,332,282,249,212,249,212,166,141,3,125,2344,2344,1563],
[292,307,349,297,262,223,262,223,175,149],
[308,335,356,303,267,227,267,227,178,151],
[336,359,364,309,273,232,273,232,182,155],
[360,391,382,325,287,244,287,244,191,162],
[392,415,398,338,299,254,299,254,199,169],
[416,460,416,354,312,265,312,265,208,177],
[461,520,472,401,354,301,354,301,236,201],
[521,590,496,422,372,316,372,316,248,211],
[591,1024,544,462,408,347,408,347,272,231]
]

prisnamnnorr = [
    "min",
    "max",
    "Norrlandsresan Vuxen Kontant",
    "Norrlandsresan Vuxen Reskassa",
    "Norrlandsresan Senior Kontant",
    "Norrlandsresan Senior Reskassa",
    "Norrlandsresan Barn Kontant",
    "Norrlandsresan Barn Reskassa",
    "Norrlandsresan Ungdom Kontant",
    "Norrlandsresan Ungdom Reskassa",
    "Norrlandsresan Vuxen periodkort 30 dagar",
    "Norrlandsresan Senior periodkort 30 dagar",
    "Norrlandsresan Senior periodkort 30 dagar",
    "Norrlandsresan Ungdom periodkort 30 dagar",
    "",
    ""
    ]

def distance(orgin,dest): 
    distance = geodesic((orgin["lat"],orgin["lon"]),(dest["lat"],dest["lon"])).km
    return distance*1.172

def StopIdToData(id):
  for row in stops.execute("SELECT stop_lat,stop_lon,stop_name,stop_scbid FROM stops WHERE stop_id = %s" % id):
    lat = row[0]
    lon = row[1]
    name = row[2]
    scbid= row[3]
  return {"name":name, "lat":lat, "lon":lon, "scbid":scbid}

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
  for row in stops.execute("SELECT agency_stop_id FROM astops WHERE stop_id = %s and agency_id = 273" % id):
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
    itravelCats = {
        "VU":"Vuxen",
        "BA":"Barn",
        "UN":"Ungdom",
        "SE":"Senior"
    }
    orgin = StopIdToData(search["route"][0]["stopId"])
    dest = StopIdToData(search["route"][-1]["stopId"])
    dist = distance(orgin,dest)
    if orgin["scbid"][0:2] == dest["scbid"][0:2]:
      priser = lpriser
      prisnamn = lprisnamn
    else:
      priser = nrrpriser
      prisnamn = prisnamnnorr
    for pricerow in priser:
      if pricerow[0]-1 <= dist and pricerow[1] >= dist:
        prisdata = pricerow
    products = []
    trips = [1]
    for trip in trips:
        pricelist = []
        for i, price in enumerate(prisdata):
          pris = float(price)
          if itravelCats[search["travellersPerCategory"][0]["cat"]] in prisnamn[i]:
            vat = round(pris*0.06,2)
            url = "https://www.tabussen.nu/lanstrafiken/biljetter-och-priser/har-koper-du-biljetten/"
            pricelist.append({
                "productId": url,
                "productTitle": prisnamn[i],
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

run(host='127.0.0.1', port=8105, reloader=True)