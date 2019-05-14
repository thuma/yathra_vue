# !/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, json, sqlite3, datetime
from bottle import get, post, run, request

travelCats = {
  "VU":"Vuxen 26-64",
  "BO1":"Barn 0-1 år",
  "BO16":"Barn 2-16 år",
  "BO26":"Ungdom 17-25 år",
  "SU":"Student 26+",
  "PS":"Pensionär 65+", 
  "SE":"Senior 65+"
}

stops = sqlite3.connect('stops')

def TimeStampToIso(tstamp):
  return datetime.datetime.fromtimestamp(tstamp).strftime("%Y-%m-%dT%H:%M:%SZ")

def isoToTimeStamp(string):
  try:
    utc_dt = datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.%fZ')
  except:
    utc_dt = datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%SZ')
  return (utc_dt - datetime.datetime(1970, 1, 1)).total_seconds()

def StopIdToName(id):
  for row in stops.execute("SELECT stop_name FROM stops WHERE stop_id = %s" % id):
   return row[0]

@get('/api/v1/productcat/travellers')
def cats():
    return json.dumps(travelCats)

@post('/api/v1/productcat/product')
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

    cookies = {
        "JSESSIONID":"ty-TVr5eXRpPxCB_ypbmDaBOFz0Zajz1AH4EazPR.f868c9f42601",
        "JSESSIONID":"ty-TVr5eXRpPxCB_ypbmDaBOFz0Zajz1AH4EazPR.d61b543d27d7"
        }
    headers = {
      'content-type': 'application/json',
      'accept': 'application/json, text/plain, */*'
      }
    query = {
      "fromLocationName": StopIdToName(search["route"][0]["stopId"]),
      "toLocationName": StopIdToName(search["route"][1]["stopId"]),
      "producers": [
        {
          "value": "287",
          "text": "Arlanda Express",
          "selected": True
        },
        {
          "value": "310",
          "text": "BT Buss",
          "selected": True
        },
        {
          "value": "480",
          "text": "Bergkvarabuss",
          "selected": True
        },
        {
          "value": "258",
          "text": "Blekingetrafiken",
          "selected": True
        },
        {
          "value": "619",
          "text": "Blå tåget",
          "selected": True
        },
        {
          "value": "644",
          "text": "Blåklintsbuss",
          "selected": True
        },
        {
          "value": "327",
          "text": "Bus4You N",
          "selected": True
        },
        {
          "value": "818",
          "text": "Gröna tåget",
          "selected": True
        },
        {
          "value": "365",
          "text": "Härjedalingen",
          "selected": True
        },
        {
          "value": "555",
          "text": "Inlandsbanan",
          "selected": True
        },
        {
          "value": "653",
          "text": "Kustpilen",
          "selected": True
        },
        {
          "value": "626",
          "text": "Lindbergs buss",
          "selected": True
        },
        {
          "value": "812",
          "text": "MTR Express",
          "selected": True
        },
        {
          "value": "621",
          "text": "Masexpressen L",
          "selected": True
        },
        {
          "value": "361",
          "text": "Masexpressen N",
          "selected": True
        },
        {
          "value": "328",
          "text": "Nettbuss express N",
          "selected": True
        },
        {
          "value": "391",
          "text": "Nikkaluoktaexpressen",
          "selected": True
        },
        {
          "value": "367",
          "text": "SGS bussen",
          "selected": True
        },
        {
          "value": "74",
          "text": "SJ",
          "selected": True
        },
        {
          "value": "275",
          "text": "SL",
          "selected": True
        },
        {
          "value": "381",
          "text": "Saga Rail",
          "selected": True
        },
        {
          "value": "815",
          "text": "Scandibuss",
          "selected": True
        },
        {
          "value": "642",
          "text": "Skaraborgaren",
          "selected": True
        },
        {
          "value": "823",
          "text": "SkiExpress",
          "selected": True
        },
        {
          "value": "380",
          "text": "Snälltåget",
          "selected": True
        },
        {
          "value": "645",
          "text": "Snötåget",
          "selected": True
        },
        {
          "value": "832",
          "text": "Svenska Buss",
          "selected": True
        },
        {
          "value": "690",
          "text": "Swebus",
          "selected": True
        },
        {
          "value": "821",
          "text": "Söne Buss",
          "selected": True
        },
        {
          "value": "358",
          "text": "Tapanis buss",
          "selected": True
        },
        {
          "value": "604",
          "text": "Trosabussen",
          "selected": True
        },
        {
          "value": "612",
          "text": "Tågab L",
          "selected": True
        },
        {
          "value": "586",
          "text": "Tågab N",
          "selected": True
        },
        {
          "value": "315",
          "text": "Tågkompaniet",
          "selected": True
        },
        {
          "value": "513",
          "text": "Tågkompaniet Norrtåg",
          "selected": True
        },
        {
          "value": "251",
          "text": "UL",
          "selected": True
        },
        {
          "value": "279",
          "text": "Västtrafik",
          "selected": True
        },
        {
          "value": "357",
          "text": "Ybuss",
          "selected": True
        },
        {
          "value": "300",
          "text": "Öresundståg",
          "selected": True
        }
      ],
      "acceptableTravelMethods": [
        {
          "value": "X2_J",
          "text": "SJ Snabbtåg",
          "selected": True
        },
        {
          "value": "EX_J",
          "text": "MTR Express",
          "selected": True
        },
        {
          "value": "EX_B",
          "text": "MTR Express (Ersättningsbuss)",
          "selected": True
        },
        {
          "value": "AX_J",
          "text": "Flygtransfer",
          "selected": True
        },
        {
          "value": "AX_B",
          "text": "Flygtransfer (Buss)",
          "selected": True
        },
        {
          "value": "XBN_B",
          "text": "Expressbuss",
          "selected": True
        },
        {
          "value": "IC_J",
          "text": "InterCity",
          "selected": True
        },
        {
          "value": "IC_B",
          "text": "InterCity (Ersättningsbuss)",
          "selected": True
        },
        {
          "value": "IC_T",
          "text": "InterCity (Ersättningstaxi)",
          "selected": True
        },
        {
          "value": "LT_J",
          "text": "Länståg",
          "selected": True
        },
        {
          "value": "LT_B",
          "text": "Länsbuss",
          "selected": True
        },
        {
          "value": "LT_F",
          "text": "Länsfärja",
          "selected": True
        },
        {
          "value": "LT_T",
          "text": "Länstaxi",
          "selected": True
        },
        {
          "value": "NT_J",
          "text": "Nattåg",
          "selected": True
        },
        {
          "value": "PT_J",
          "text": "Pågatåg",
          "selected": True
        },
        {
          "value": "PT_B",
          "text": "Pågatåg  (Ersättningsbuss)",
          "selected": True
        },
        {
          "value": "RE_J",
          "text": "Regional",
          "selected": True
        },
        {
          "value": "RE_B",
          "text": "Regional (Buss)",
          "selected": True
        },
        {
          "value": "TIB_B",
          "text": "Tåg i Bergslagen (Ersätt.buss)",
          "selected": True
        },
        {
          "value": "TIB_J",
          "text": "Tåg i Bergslagen",
          "selected": True
        },
        {
          "value": "SP_J",
          "text": "Specialtåg",
          "selected": True
        },
        {
          "value": "LT_S",
          "text": "Spårvagn",
          "selected": True
        },
        {
          "value": "LT_U",
          "text": "Tunnelbana",
          "selected": True
        },
        {
          "value": "_B",
          "text": "Tågbuss",
          "selected": True
        },
        {
          "value": "_T",
          "text": "Tågtaxi",
          "selected": True
        },
        {
          "value": "_J",
          "text": "Övriga tåg",
          "selected": True
        },
        {
          "value": "_F",
          "text": "Färja",
          "selected": True
        },
        {
          "value": "AVE_J",
          "text": "AVE",
          "selected": True
        },
        {
          "value": "EC_J",
          "text": "EuroCity",
          "selected": True
        },
        {
          "value": "EST_J",
          "text": "Eurostar",
          "selected": True
        },
        {
          "value": "ICE_J",
          "text": "InterCity (ICE)",
          "selected": True
        },
        {
          "value": "ICL_J",
          "text": "InterCity Lyn",
          "selected": True
        },
        {
          "value": "IR_J",
          "text": "InterRegio",
          "selected": True
        },
        {
          "value": "T20_J",
          "text": "Talgo 200",
          "selected": True
        },
        {
          "value": "THA_J",
          "text": "Thalys",
          "selected": True
        },
        {
          "value": "TGV_J",
          "text": "TGV",
          "selected": True
        },
        {
          "value": "TGV_B",
          "text": "TGV (Ersättningsbuss)",
          "selected": True
        },
        {
          "value": "UT_F",
          "text": "Utrikes färja",
          "selected": True
        }
      ],
      "travelDate": search["temporal"]["earliestDepature"],
      "travelDateAsString": search["temporal"]["earliestDepature"][0:10] + " " + search["temporal"]["earliestDepature"][12:19],
      "maxNumberOfChanges": "7"
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
		
    products = []
    for p in result.json():
      pricelist = []
      for price in p["salesCategories"]:
		pricelist.append({
            "productId": p["uniqueIdentifier"],
			"productTitle": price["itineraryPriceGroupChoices"][0]["priceGroupCode"]["text"],
            "productDescription": price["flex"]["text"],
            "fares": [
                {
                    "amount": float(price["totalPrice"]["value"]),
                    "currency": "SEK",
                    "vatAmount": round(float(price["totalPrice"]["value"])*0.06,2),
                    "vatPercent": 6
                }
            ],
            "productProperties": {
                "date": TimeStampToIso(p["departureDateTime"]/1000)
            },
            "travellersPerCategory": search["travellersPerCategory"]
        })
      products.append(pricelist)
    return json.dumps(products)

run(host='0.0.0.0', port=8080, reloader=True)