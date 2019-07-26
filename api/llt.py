# !/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, json
from bottle import get, post, run, request, response

travelCats = {
    "BA":"Barn (7-19 år)",
    "UN":"Ungdom (20-25 år)",
    "VU":"Vuxen (26-64 år)",
    "PE":"Pensionär (65-74 år)",
    "SE":"Senior (75- år)"
}

priser = [
    ["Enkelbiljett/värdekvitto",22,35,35,35,35],
    ["Enkel resa med reskassa",13,19,24,19,13],
    ["Enkel resa köp i app",15,28,28,28,28],
    ["Periodkort 30 dagar",340,500,670,500,340],
    ["Periodkort 90 dagar",910,1340,1800,1340,910],
    ["Periodkort 180 dagar",1680,2500,3320,2500,1680],
    ["Årskort",2850,4240,5630,4240,2850],
    ["72 h",150,150,150,150,150]
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
        "BA":1,
        "UN":2,
        "VU":3,
        "PE":4,
        "SE":5
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

run(host='127.0.0.1', port=8107, reloader=True)
