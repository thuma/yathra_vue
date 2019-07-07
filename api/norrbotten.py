# !/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, json, sqlite3, datetime, urllib, rt90, math, re
from bottle import get, post, run, request, response
from dateutil import parser, tz

travelCats = {
    "VU":"Vuxen",
    "ST":"Skolungdom",
    "UN":"Ungdom",
    "SE":"Senior"
}

stops = sqlite3.connect('../static_data/stops')

priser = [
[0,10,28,25,21,19,14,13,53,40,27,252,189,126,448,336,224,672,616],
[11,20,44,40,33,30,22,20,84,63,42,396,297,198,704,528,352,1056,968],
[21,30,54,49,41,36,27,24,103,77,51,486,365,243,864,648,432,1296,1188],
[31,40,74,67,56,50,37,33,141,105,70,666,500,333,1184,888,592,1776,1628],
[41,50,87,78,65,59,44,39,165,124,83,783,587,392,1392,1044,696,2088,1914],
[51,60,102,92,77,69,51,46,194,145,97,918,689,459,1632,1224,816,2448,2244],
[61,70,117,105,88,79,59,53,222,167,111,1053,790,527,1872,1404,936,2808,2574],
[71,80,128,115,96,86,64,58,243,182,122,1152,864,576,2048,1536,1024,3072,2816],
[81,90,142,128,107,96,71,64,270,202,135,1278,959,639,2272,1704,1136,3408],
[91,100,158,142,119,107,79,71,300,225,150,1422,1067,711,2528,1896,1264,3792],
[101,110,171,154,128,115,86,77,325,244,162,1539,1154,770,2736,2052,1368,4104],
[111,120,183,165,137,124,92,82,348,261,174,1647,1235,824,2928,2196,1464,4392],
[121,130,197,177,148,133,99,89,374,281,187,1773,1330,887,3152,2364,1576,4728],
[131,140,211,190,158,142,106,95,401,301,200,1899,1424,950,3376,2532,1688,5064],
[141,150,223,201,167,151,112,100,424,318,212,2007,1505,1004,3568,2676,1784,5352],
[151,160,237,213,178,160,119,107,450,338,225,2133,1600,1067,3792,2844,1896,5688],
[161,170,248,223,186,167,124,112,471,353,236,2232,1674,1116,3968,2976,1984,5952],
[171,180,261,235,196,176,131,117,496,372,248,2349,1762,1175,4176,3132,2088,6264],
[181,190,273,246,205,184,137,123,519,389,259,2457,1843,1229,4368,3276,2184,6552],
[191,200,286,257,215,193,143,129,543,408,272,2574,1931,1287,4576,3432,2288,6864],
[201,210,298,268,224,201,149,134,566,425,283,2682,2012,1341,4768,3576,2384,7152],
[211,220,310,279,233,209,155,140,589,442,295,2790,2093,1395,4960,3720,2480,7440],
[221,230,319,287,239,215,160,144,606,455,303,2871,2153,1436,5104,3828,2552,7656],
[231,240,332,299,249,224,166,149,631,473,315,2988,2241,1494,5312,3984,2656,7968],
[241,250,343,309,257,232,172,154,652,489,326,3087,2315,1544,5488,4116,2744,8232],
[251,260,352,317,264,238,176,158,669,502,334,3168,2376,1584,5632,4224,2816,8448],
[261,270,362,326,272,244,181,163,688,516,344,3258,2444,1629,5792,4344,2896,8688],
[271,280,371,334,278,250,186,167,705,529,352,3339,2504,1670,5936,4452,2968,8904],
[281,290,380,342,285,257,190,171,722,542,361,3420,2565,1710,6080,4560,3040,9120],
[291,300,389,350,292,263,195,175,739,554,370,3501,2626,1751,6224,4668,3112,9336],
[301,310,398,358,299,269,199,179,756,567,378,3582,2687,1791,6368,4776,3184,9552],
[311,320,406,365,305,274,203,183,771,579,386,3654,2741,1827,6496,4872,3248,9744],
[321,330,413,372,310,279,207,186,785,589,392,3717,2788,1859,6608,4956,3304,9912],
[331,340,423,381,317,286,212,190,804,603,402,3807,2855,1904,6768,5076,3384,10152],
[341,350,429,386,322,290,215,193,815,611,408,3861,2896,1931,6864,5148,3432,10296],
[351,360,436,392,327,294,218,196,828,621,414,3924,2943,1962,6976,5232,3488,10464],
[361,370,444,400,333,300,222,200,844,633,422,3996,2997,1998,7104,5328,3552,10656],
[371,380,455,410,341,307,228,205,865,648,432,4095,3071,2048,7280,5460,3640,10920],
[381,390,461,415,346,311,231,207,876,657,438,4149,3112,2075,7376,5532,3688,11064],
[391,400,470,423,353,317,235,212,893,670,447,4230,3173,2115,7520,5640,3760,11280],
[401,478,430,359,323,239,215,908,681,454,4302,3227,2151,7648,5736,3824,11472]
]

prisnamn = [
    "min",
    "max",
    "Vuxen Kontant",
    "Vuxen Reskassa",
    "Ungdom/Senior Kontant",
    "Ungdom/Senior Reskassa",
    "Skolungdom Kontant",
    "Skolungdom Reskassa",
    "Vuxen Tur&Retur",
    "Ungdom/Senior Tur&Retur",
    "Skolungdom Tur&Retur",
    "Vuxen 10-resor",
    "Ungdom/Senior 10-resor",
    "Skolungdom 10-resor",
    "Vuxen 20-resor",
    "Ungdom/Senior 20-resor",
    "Skolungdom 20-resor",
    "Vuxen 40-resor",
    "",
    ""
    ]

def distance(orgin,dest): 
    # approximate radius of earth in km
    R = 6373.0

    lat1 = math.radians(orgin["lat"])
    lon1 = math.radians(orgin["lon"])
    lat2 = math.radians(dest["lat"])
    lon2 = math.radians(dest["lon"])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

def StopIdToData(id):
  for row in stops.execute("SELECT stop_lat,stop_lon,stop_name,stop_scbid FROM stops WHERE stop_id = %s" % id):
    lat = row[0]
    lon = row[1]
    name = row[2]
  return {"name":name, "lat":lat, "lon":lon}

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
        "ST":"Skolungdom",
        "UN":"Ungdom",
        "SE":"Senior"
    }
    orgin = StopIdToData(search["route"][0]["stopId"])
    dest = StopIdToData(search["route"][-1]["stopId"])
    dist = distance(orgin,dest)
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
            print price
            vat = round(pris*0.06,2)
            url = "https://ltnbd.se/priser-biljetter/"
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

run(host='127.0.0.1', port=8104, reloader=True)