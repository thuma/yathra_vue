# !/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, json, sqlite3, datetime, urllib, rt90
from bottle import get, post, run, request, response
from dateutil import parser, tz
from ConfigParser import ConfigParser

travelCats = {
    "VU":"Vuxen",
    "BA":"Barn (7-15 år)",
    "BY":"Barn (0-6 år)"
}

btstops = {
    "740000002":"1",  #Göteborg C
    "740000018":"2",  #Alingsås
    "740000540":"11", #Lerum
    "740000008":"3",  #Skövde C
    "740000077":"4",  #Hallsberg
    "740000099":"9",  #Västerås C
    "740000001":"5",  #Stockholm C
    "740000556":"6"   #Arlanda C
}

stops = sqlite3.connect('stops')

def TimeStampToIso(tstamp):
  return datetime.datetime.fromtimestamp(tstamp).strftime("%Y-%m-%dT%H:%M:%SZ")

def utcIsoToLocalBatagetDate(datedate):
   return (parser.parse(datedate).astimezone(tz.gettz("Europe/Stockholm"))-datetime.timedelta(minutes=10)).strftime("%Y-%m-%d")

def StopIdToData(id):
  for row in stops.execute("SELECT stop_lat,stop_lon,stop_name FROM stops WHERE stop_id = %s" % id):
    lat = row[0]
    lon = row[1]
    name = row[2]
  return {"name":name, "lat":lat, "lon":lon, "id":btstops[id]}
 
@post('/api/v1/buy')
def cats():
    response.content_type = 'application/json'
    returndata = {"payUrl":"https://www.blataget.com/sv/#searchsmall"}
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
        "fromstation":fromdata["id"],
        "tostation":todata["id"],
        "ticketclass1":"1",
        "ticketclass2":"0",
        "ticketclass3":"0",
        "notodate":"1",
        "todate":"",
        "fromdate":utcIsoToLocalBatagetDate(search["temporal"]["earliestDepature"])
    }
    
    for cat in search["travellersPerCategory"]:
        if cat['cat'] == "VU":
            data["ticketclass1"] = cat['tra']
        if cat['cat'] == "BA":
            data["ticketclass2"] = cat['tra']
        if cat['cat'] == "BY":
            data["ticketclass3"] = cat['tra']
    location = requests.post("https://www.blataget.com/sv/ajax/orderingprocess/", data=data)
    data = location.content.split('class="selectprice"')
    del data[0]
    products = []
    for trip in data:
        pricelist = []
        url = "https://www.blataget.com/sv/#searchsmall"
        pris = float(trip.split(">")[1].split("<")[0])
        vat = pris*0.06
        pricelist.append({
            "productId": url,
            "productTitle": "Biljett",
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
    products.append(pricelist)
    response.content_type = 'application/json'
    return json.dumps(products)

run(host='127.0.0.1', port=8093, reloader=True)
