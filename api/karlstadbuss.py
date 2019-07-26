# !/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, json
from bottle import get, post, run, request, response

travelCats = {
    "BA":"Barn och skolungdom (0 - 19 år)",
    "UN":"Ungdom (20-25 år)",
    "VU":"Vuxen (26-64 år)",
    "SE":"Senior (65 - år)",
    "SL":"Senior (65 - år) reser mellan 10-14",
    "FA":"Duo (5 pers. var av 1 eller 2 fyllda 19 år)",
    "ST":"Student minst 75% (26 - 64 år)"
}

priser = [
    ["Enkelbiljett reskassa",                41,18,21,18,13,18,13],
    ["Enkelbiljett förköp app/automat/butik",49,24,26,24,24,24,16],
    ["Enkelbiljett ombord med kort",         75,45,45,45,45,45,45]
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
        "FA":1,
        "UN":2,
        "VU":3,
        "SE":4,
        "SL":5,
        "ST":6,
        "BA":7
    }
    products = []
    trips = [1]
    for trip in trips:
        pricelist = []
        for price in priser:
          pris = float(price[itravelCats[search["travellersPerCategory"][0]["cat"]]])
          vat = round(pris*0.06,2)
          url = "https://www.llt.lulea.se/priser-och-busskort/busskort/"
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

run(host='127.0.0.1', port=8109, reloader=True)
