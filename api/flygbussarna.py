 # !/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, json, sqlite3, datetime, urllib, math
from bottle import get, post, run, request, response
from dateutil import parser, tz
from urllib import urlencode, quote_plus
from ConfigParser import ConfigParser

travelCats = {
    "VU":"Vuxen",
    "UN":"Ungdom (8-17 år)"
}

pricedata = {"740000554":{ #GOT
    "VU":{"productTitle":"Enkel Vuxen","amount":99},
    "UN":{"productTitle":"Enkel Ungdom (8-17 år)","amount":89},
  },
  "740020671":{  #ARN
    "VU":{"productTitle":"Enkel Vuxen","amount":99},
    "UN":{"productTitle":"Enkel Ungdom (8-17 år)","amount":89},
  },
  "740033206":{  #ARN
    "VU":{"productTitle":"Enkel Vuxen","amount":99},
    "UN":{"productTitle":"Enkel Ungdom (8-17 år)","amount":89},
  },
  "740043310":{  #ARN
    "VU":{"productTitle":"Enkel Vuxen","amount":99},
    "UN":{"productTitle":"Enkel Ungdom (8-17 år)","amount":89},
  },
  "740000953":{  #MMO
    "VU":{"productTitle":"Enkel Vuxen","amount":105},
    "UN":{"productTitle":"Enkel Ungdom (8-17 år)","amount":85},
  },
  "740011384":{  #SKAVSTA
    "VU":{"productTitle":"Enkel Vuxen","amount":159},
    "UN":{"productTitle":"Enkel Ungdom (8-17 år)","amount":139},
  },
  "740026020":{  #Visby
    "VU":{"productTitle":"Enkel Vuxen","amount":50},
    "UN":{"productTitle":"Enkel Ungdom (8-17 år)","amount":50},
  },
  "740024556":{  #Västerås
    "VU":{"productTitle":"Enkel Vuxen","amount":159},
    "UN":{"productTitle":"Enkel Ungdom (8-17 år)","amount":139},
  }
}

@post('/api/v1/buy')
def cats():
    response.content_type = 'application/json'
    returndata = {"payUrl":"https://www.flygbussarna.se/"}
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
    if search["route"][-1]["stopId"] in pricedata:
        thisdata = pricedata[search["route"][-1]["stopId"]][search["travellersPerCategory"][0]["cat"]]
    elif search["route"][0]["stopId"] in pricedata:
        thisdata = pricedata[search["route"][0]["stopId"]][search["travellersPerCategory"][0]["cat"]]
    else:
      return json.dumps([[]])

    products = []
    pricelist = []

    pricelist.append({
            "productId": "single",
            "productTitle": thisdata["productTitle"],
            "fares": [
                {
                    "amount": thisdata["amount"],
                    "currency": "SEK",
                    "vatAmount": round(thisdata["amount"] * 0.06,2),
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

run(host='127.0.0.1', port=8110, reloader=True)


#Liljeholmen/Bromma/Kista/Sundbyberg Arlanda
#  Enkel Vuxen 119 kr
#  Enkel Ungdom (8-17 år) 109 kr


#Skavsta norrköping
#  Enkel Vuxen 139 kr
#  Enkel Ungdom (8-17 år) 125 kr

