# !/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, json
from bottle import get, post, run, request, response

travelCats = {
    "VU":"Vuxen (26- år)",
    "BA":"Barn (7-19 år)",
    "UN":"Ungdom (20-25 år)",
    "FE":"Resenärer på Buss 629"
}

priser = [
  ["Enkel biljett",28,14,21,0],
  ["Enkel biljett Mobilapp och reskassa",25,13,19,0],
  ["Tur och retur",53,27,40,0],
  ["10 resor",252,126,189,0],
  ["20 resor",448,224,336,0],
  ["40 resor",672,672,672,0],
  ["Periodkort 30 dagar",616,616,616,0]
]

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
        "VU":1,
        "BA":2,
        "UN":3,
        "FE":4
    }
    products = []
    trips = [1]
    for trip in trips:
        pricelist = []
        for price in priser:
          pris = float(price[itravelCats[search["travellersPerCategory"][0]["cat"]]])
          vat = round(pris*0.06,2)
          url = "https://www.citybuss.se/pris-information/"
          pricelist.append({
                "productId": url,
                "productTitle": price[0],
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

run(host='127.0.0.1', port=8108, reloader=True)
