# !/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, json, sqlite3, datetime, urllib, rt90, math, re
from bottle import get, post, run, request, response
from dateutil import parser, tz

travelCats = {
     "VU":"Vuxen",
     "UN1":"Ungdom 7-19år",
     "UN2":"Ungdom 20-25år",
     "ST":"Student",
     "FT":"Förmånstagare"
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
  for gtfsdata in stops.execute("SELECT stop_lon, stop_lat FROM stops WHERE stop_id = %s" % id):
    dist = 99999.0;
    for row in stops.execute("SELECT stop_lon, stop_lat, agency_stop_id, agency_stop_name FROM akstops WHERE stop_lon BETWEEN %s AND %s AND stop_lat BETWEEN %s AND %s AND agency_id = 268" % (gtfsdata[0]-0.5,gtfsdata[0]+0.5,gtfsdata[1]-0.5,gtfsdata[1]+0.5)):
        meters = distance({"lat":row[1],"lon":row[0]},{"lat":gtfsdata[1],"lon":gtfsdata[0]})
        if meters < dist:
            dist = meters
            best = row
    return str(best[3].encode("utf8")+"|"+str(best[2])+"|0")

def distance(orgin,dest): 
    # approximate radius of earth in km
    R = 6373000

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
        "inpPointFr_ajax":StopIdToName(search["route"][0]["stopId"]),
        "inpPointTo_ajax":StopIdToName(search["route"][-1]["stopId"]),
        "inpPointInterm_ajax":"inpPointInterm_ajax",
        #"inpPointFr":"Mora resecentrum (Mora)",
        #"inpPointTo":"Orsa busstn (Orsa)",
        "selDirection":"0",
        "inpTime":utcIsoToLocalSktrTime(search["temporal"]["earliestDepature"]),
        "inpDate":utcIsoToLocalSktrDate(search["temporal"]["earliestDepature"]),
        "x":"24",
        "y":"2",
        "selPriceType":"0",
        "cmdAction":"search",
        "EU_Spirit":"False",
        "TNSource":"XTRAFIKEN",
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
        #"selPointFr":"Mora resecentrum (Mora)|562152|0",
        #"selPointTo":"Orsa busstn (Orsa)|534063|0",
        #"selPointFrKey":"562152",
        #"selPointToKey":"534063",
        "selPointInterm":"inpPointInterm_ajax",
        "selPointIntermKey":"",
        "TrafficMask":"1,2,4,8,32,",
        "RSH":"",
        #"FirstStart":"2019-06-19 07:45:00",
        #"LastStart":"2019-06-19 09:45:00",
        "FirstStart2":"",
        "LastStart2":"",
        "CacheFile":"155632812245320541",
        "CacheFile2":"",
        "CacheFileSingleStation":"",
        #"inpDate2":"2019-06-19",
        #"inpTime2":"11:48",
        "selDirection2":"0",
        "selSingleStation":"",
        "selSingleStationKey":"",
        "selComboJourney":"0",
        "chkWalkToOtherStop":"0",
        #"inpDateSingleStation":"2019-06-19",
        #"inpTimeSingleStation":"07:48",
        "selDirectionSingleStation":"0",
        "Source":"resultspage",
        "HtmlSource":"",
        "inpSender":""
    }
    print data["inpPointFr_ajax"]
    print data["inpPointTo_ajax"]
    result = requests.get(
        "https://reseplanerare.fskab.se/xtrafiken/v3/querypage_adv.aspx",
        data = data
        )
    trips = [1]
    products = []

    names = [
"Mobil/Reskassa Vuxen",
"Mobil/Reskassa 20-25år/Stud",
"Mobil/Reskassa 7-19år/Förmån",
"30-dagarsbiljett Vuxen",
"30-dagarsbiljett 20-25år/Stud",
"30-dagarsbiljett 7-19år/Förmån",
"Årsbiljett Vuxen",
"Årsbiljett 20-25år/Stud",
"Årsbiljett 7-19år/Förmån",
"",
"",
"",
"",
"",
""
    ]

    itravelCats = {
     "VU":"Vuxen",
     "UN1":"7-19år",
     "UN2":"20-25år",
     "ST":"Stud",
     "FT":"Förmån"
    }

    for trip in trips:
        pricelist = []
        prices = eval("["+result.content.split("priceArr[")[1].split("(")[1].split(")")[0]+"]")
        for i, price in enumerate(prices):
          if itravelCats[search["travellersPerCategory"][0]["cat"]] in names[i]:
            print price
            pris = float(re.sub('[^0-9\,]','', price).replace(",","."))
            vat = round(pris*0.06,2)
            url = "https://xtrafik.se/biljetter-och-priser"
            pricelist.append({
                "productId": url,
                "productTitle": names[i],
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

run(host='127.0.0.1', port=8101, reloader=True)