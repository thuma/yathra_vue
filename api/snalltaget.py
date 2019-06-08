# !/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, json, sqlite3, datetime, urllib, dateutil
from bottle import get, post, run, request, response
from dateutil import parser, tz
from os import popen
from time import sleep

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

def stringToUnixTS(string):
  utc_dt = parser.parse(string).astimezone(tz.tzutc());
  return (utc_dt - datetime.datetime(1970, 1, 1, tzinfo=tz.tzutc())).total_seconds()

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
 
    travelers = []
    for traveler in search["travellersPerCategory"]:
      for a in range(traveler["tra"]):
        travelers.append({
          "travellerCategory":traveler["cat"]
        })
   
    query = {
        "departureLocationId":int(search["route"][0]["stopId"][2:]),
        "departureLocationProducerCode":int(search["route"][0]["stopId"][0:2]),
        "arrivalLocationId":int(search["route"][1]["stopId"][2:]),
        "arrivalLocationProducerCode":int(search["route"][1]["stopId"][0:2]),
        "departureDateTime":search["temporal"]["earliestDepature"][0:10]+"<space>00:00",
        "travelType":"T",
        "promotionCode":"null",
        "passengers":travelers
    }
    
    querydata = json.dumps(query).replace('"null"',"null").replace(" ","").replace("<space>"," ");

    #bcmd = "curl -s 'https://www.snalltaget.se/boka-biljett' -H 'Connection: keep-alive' -H 'Pragma: no-cache' -H 'Cache-Control: no-cache' -H 'Origin: https://www.snalltaget.se' -H 'Upgrade-Insecure-Requests: 1' -H 'Content-Type: application/x-www-form-urlencoded' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3' -H 'Referer: https://www.snalltaget.se/' -H 'Accept-Encoding: gzip, deflate, br' -H 'Accept-Language: sv-SE,sv;q=0.9,en-US;q=0.8,en;q=0.7,es;q=0.6' -H 'Cookie: "+kaka+";' --data 'from=1&to=2&t=T&date=2019-08-23T00%3A00%3A00&rdate=2019-08-23T00%3A00%3A00&rt=VU&ra=-1' --compressed"
    #bdata = popen(bcmd).read()
    #auth = "Bearer "+bdata.split("window.Bokning.ApiToken")[1].split("'")[1]

    cmd  = '''curl -s 'https://www.snalltaget.se/api/timetables' -H 'Pragma: no-cache' -H 'Origin: https://www.snalltaget.se' -H 'Accept-Encoding: gzip, deflate, br' -H 'Accept-Language: sv' -H 'Authorization: Bearer irO4mN3R8f2A0-KND1KoO1wf2wQ0cNeMU6SVM9mUCCLA_DBJNcJzCaL2p6JlLiTvzvkytnZrvElgjDLEXbBe5l1PXWmNVFRHdq-cSXa1V4LLdiCIH1AXOqaAwHoOrXZV0n_IHC9dpNlT9X4Hk7iiEpIl620YHZG3PcsSiOEkiYi9Gs7rtmtkCP8owW8O304Y_Z-MZt_Yx3ovQepTiOMT2Qoc_UNjPNASXdc4tA1UZfYfPfRQitESjJRiLZ6BCvV626gv2X3eqtfMrYoCLFxp1AwB72PUQvc2ewUYJO-Ic-79BWt93WkxCBA66SOvFXeFnN1supFfBxY8KhI1ZRLVgwsY7vLXd1HI4O7HTNZMgd_FLNIeApvKrsTL8Xb8Ya_WM7mVYfw_kiDtqQmzlYw1Iw' -H 'Content-Type: application/json;charset=UTF-8' -H 'Accept: application/json, text/plain, */*' -H 'Cache-Control: no-cache' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36' -H 'Connection: keep-alive' -H 'Referer: https://www.snalltaget.se/boka-biljett' --data-binary '%s' --compressed''' % querydata 
    print cmd
    tdata = popen(cmd).read()
    print tdata
    result = json.loads(tdata)
        
    trips = []

    refs = []
    for j in result["journeyAdvices"]:
      if stringToUnixTS(j["departureDateTime"]) >= isoToTimeStamp(search["temporal"]["earliestDepature"]):
        if stringToUnixTS(j["arrivalDateTime"]) <= isoToTimeStamp(search["temporal"]["latestArrival"]):
          trips.append(j)
          refs.append(j["journeyConnectionReference"])

    price = {
        "timetableId":result["id"],
        "journeyConnectionReferences":refs
    }
    sleep(5)
    pricequery = json.dumps(price).replace(" ","")
    cmd2 ='''curl -s 'https://www.snalltaget.se/api/journeyadvices/lowestprices' -H 'Pragma: no-cache' -H 'Origin: https://www.snalltaget.se' -H 'Accept-Encoding: gzip, deflate, br' -H 'Accept-Language: sv' -H 'Authorization: Bearer irO4mN3R8f2A0-KND1KoO1wf2wQ0cNeMU6SVM9mUCCLA_DBJNcJzCaL2p6JlLiTvzvkytnZrvElgjDLEXbBe5l1PXWmNVFRHdq-cSXa1V4LLdiCIH1AXOqaAwHoOrXZV0n_IHC9dpNlT9X4Hk7iiEpIl620YHZG3PcsSiOEkiYi9Gs7rtmtkCP8owW8O304Y_Z-MZt_Yx3ovQepTiOMT2Qoc_UNjPNASXdc4tA1UZfYfPfRQitESjJRiLZ6BCvV626gv2X3eqtfMrYoCLFxp1AwB72PUQvc2ewUYJO-Ic-79BWt93WkxCBA66SOvFXeFnN1supFfBxY8KhI1ZRLVgwsY7vLXd1HI4O7HTNZMgd_FLNIeApvKrsTL8Xb8Ya_WM7mVYfw_kiDtqQmzlYw1Iw' -H 'Content-Type: application/json;charset=UTF-8' -H 'Accept: application/json, text/plain, */*' -H 'Cache-Control: no-cache' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36' -H 'Connection: keep-alive' -H 'Referer: https://www.snalltaget.se/boka-biljett' --data-binary '%s' --compressed''' % pricequery
    print cmd2
    pdata = popen(cmd2).read()
    presult = json.loads(pdata)
    print presult
    params = {
        "from": query["departureLocationId"],
        "to": query["arrivalLocationId"],
        "t": "T",
        "date": search["temporal"]["earliestDepature"][0:10]+"T00:00:00", 
        "rdate": search["temporal"]["earliestDepature"][0:10]+"T00:00:00",
        "rt": "VU",
        "ra": -1
    }

    products = []
    for p in presult:
      pricelist = []
      pris = float(p["lowestTotalPrice"])
      pricelist.append({
            "productId": "specialID",
            "productTitle": "Lägsta pris",
            "productDescription": "Lägsta mjliga pris",
            "fares": [
                {
                    "amount": pris,
                    "currency": "SEK",
                    "vatAmount": round(pris*0.06,2),
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

run(host='127.0.0.1', port=8091, reloader=True)

