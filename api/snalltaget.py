snalltaget
# !/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, json, sqlite3, datetime, urllib
from bottle import get, post, run, request, response

travelCats = {
  "VU":"Vuxen",
  "BO":"Barn/Ungdom",
  "SU":"Student",
  "SE":"Senior"
}

def TimeStampToIso(tstamp):
  return datetime.datetime.fromtimestamp(tstamp).strftime("%Y-%m-%dT%H:%M:%SZ")

def isoToTimeStamp(string):
  try:
    utc_dt = datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.%fZ')
  except:
    utc_dt = datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%SZ')
  return (utc_dt - datetime.datetime(1970, 1, 1)).total_seconds()

def StopIdToName(id):
  if id in stopids:
    return stopids[id].decode("utf-8")
  for row in stops.execute("SELECT stop_name FROM stops WHERE stop_id = %s" % id):
   return row[0]

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

    headers = {
      'content-type': 'application/json'
      }
    query = {
      }

    result = requests.post(
        "https://www.tagbokningen.se/will/api/rest/timetable/searchTimetable",
        data=json.dumps(query),
        headers=headers,
        cookies=cookies
        )

    trips = []
    for j in result.json()["journeyAdvices"]:
      if j["departureDateTime"]/1000 >= isoToTimeStamp(search["temporal"]["earliestDepature"]):
        if j["arrivalDateTime"]/1000 <= isoToTimeStamp(search["temporal"]["latestArrival"]):
          trips.append(j)

    travelers = []
    for traveler in search["travellersPerCategory"]:
      for a in range(traveler["tra"]):
        travelers.append({
          "travellerCategory": {
            "value": traveler["cat"]
          },
          "travellerAge": traveler["age"],
          "travellerAgeRange": False
        })

    price = {
      "journeyAdvices": trips,
      "travellers": travelers
    }

    result = requests.post(
        "https://www.tagbokningen.se/will/api/rest/gts/getPrice",
        data=json.dumps(price),
        headers=headers,
        cookies=cookies
        )

    url = "https://www.sj.se/#/tidtabell/"
    url = url + urllib.quote(urllib.quote(StopIdToName(search["route"][0]["stopId"]).encode('utf-8'))) + "/"
    url = url + urllib.quote(urllib.quote(StopIdToName(search["route"][1]["stopId"]).encode('utf-8'))) + "/enkel/avgang/"
    url = url + search["temporal"]["earliestDepature"].replace("-","").replace("T","-").replace(":","")[0:13] + "/avgang/"
    url = url + search["temporal"]["earliestDepature"].replace("-","").replace("T","-").replace(":","")[0:13]+"/VU--///0//"
    products = []
	
    for p in result.json():
      pricelist = []
      for price in p["salesCategories"]:
        pris = float(price["totalPrice"]["value"])
        if pris <= 200:
            pris = pris - 25
        elif pris <= 300:
            pris = pris - 22
        elif pris > 300:
            pris = round(pris*0.946,0)
        pricelist.append({
            "productId": url,
            "productTitle": price["itineraryPriceGroupChoices"][0]["priceGroupCode"]["text"],
            "productDescription": price["flex"]["text"],
            "fares": [
                {
                    "amount": pris,
                    "currency": "SEK",
                    "vatAmount": round(pris*0.06,2),
                    "vatPercent": 6
                }
            ],
            "productProperties": {
                "date": TimeStampToIso(p["departureDateTime"]/1000)
            },
            "travellersPerCategory": search["travellersPerCategory"]
        })
      products.append(pricelist)
    response.content_type = 'application/json'
    return json.dumps(products)

run(host='0.0.0.0', port=8085, reloader=True)

curl 'https://www.snalltaget.se/api/timetables' -H 'Content-Type: application/json;charset=UTF-8' --data-binary '{"departureLocationId":1,"departureLocationProducerCode":74,"arrivalLocationId":3,"arrivalLocationProducerCode":74,"departureDateTime":"2019-05-30 00:00","travelType":"T","promotionCode":null,"passengers":[{"passengerAge":null,"passengerCategory":"VU"}]}' --compressed
