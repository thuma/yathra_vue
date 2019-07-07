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

lpriser = [
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
lprisnamn = [
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
    "Norrlandsresan Ungdom Kontant",
    "Norrlandsresan Ungdom Reskassa",
    "Norrlandsresan Skolungdom Kontant",
    "Norrlandsresan Skolungdom Reskassa",
    "Norrlandsresan Vuxen periodkort 30 dagar",
    "Norrlandsresan Senior periodkort 30 dagar",
    "Norrlandsresan Senior periodkort 30 dagar",
    "Norrlandsresan Skolungdom periodkort 30 dagar",
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
        "ST":"Skolungdom",
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