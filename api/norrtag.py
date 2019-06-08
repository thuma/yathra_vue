# !/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, json, sqlite3, datetime, urllib
from bottle import get, post, run, request, response

travelCats = {
  "VU":"Vuxen",
  "BO":"Barn/Ungdom",
  "SU":"Student",
  "PS":"Pensionär",
  "SE":"Senior"
}

stopids = {
    "740000114":"Abisko turiststation",
    "740000151":"Abisko Östra",
    "740000018":"Alingsås",
    "740000004":"Alvesta",
    "740000262":"Arboga",
    "740000615":"Arbrå",
    "740000556":"Arlanda C",
    "740000221":"Arvika",
    "740001568":"Avesta centrum",
    "740000111":"Avesta Krylbo",
    "760000519":"Avesta Källhagens ind.område",
    "740000294":"Bastuträsk",
    "740000059":"Björkliden",
    "760002406":"Björnfjell",
    "740000150":"Boden C",
    "740000128":"Bollnäs",
    "740000143":"Borgstena",
    "740000160":"Borlänge C",
    "740000300":"Borås C",
    "740000526":"Brunflo",
    "740000032":"Bräcke",
    "740000660":"Bålsta",
    "860000858":"Copenhagen Airport",
    "740000129":"Degerfors",
    "740000065":"Dingle station",
    "740001333":"Dingtuna",
    "740000303":"Djurås",
    "740000308":"Duved",
    "740000096":"Emmaboda",
    "740000063":"Enafors",
    "740000072":"Enköping",
    "740000842":"Erikslund",
    "740000170":"Eskilstuna C",
    "740021552":"Eskilstuna Mälarsjukhuset",
    "740000266":"Fagersta C",
    "740020094":"Fagersta Norra",
    "740001579":"Falkenberg station",
    "740000060":"Falköping C",
    "740000030":"Falun C",
    "740000414":"Fjällåsen",
    "740000031":"Flemingsberg",
    "740000288":"Flen",
    "740000036":"Floby",
    "740000704":"Fors station",
    "760000522":"Fredrikstad",
    "740000109":"Fristad",
    "740000378":"Fränsta",
    "740000293":"Frövi",
    "740000322":"Gagnef station",
    "740000602":"Gnarp",
    "740000694":"Gnesta",
    "740000112":"Gnosjö",
    "740000217":"Grums station",
    "740000482":"Grythyttan station",
    "740000162":"Grängesberg",
    "740000107":"Grästorp",
    "740000254":"Gällivare station",
    "740000324":"Gällö",
    "740000210":"Gävle C",
    "740000002":"Göteborg C",
    "760000546":"Halden",
    "740000077":"Hallsberg",
    "740000673":"Hallstahammar station",
    "740000080":"Halmstad C",
    "740000674":"Heby station",
    "740000042":"Hedemora",
    "760001122":"Heimdal",
    "740000044":"Helsingborg C",
    "740000040":"Herrljunga",
    "740000089":"Hestra",
    "740000218":"Hofors station",
    "740000632":"Holmsveden",
    "740000630":"Horndals Bruk station",
    "740000511":"Hovmantorp",
    "740000187":"Hudiksvall",
    "740000283":"Hultsfred station",
    "740000620":"Huskvarna",
    "740001584":"Husum station",
    "740000419":"Hällefors",
    "740000738":"Hälleforsnäs",
    "740000219":"Hällnäs station",
    "740000253":"Härnösand station",
    "740000006":"Hässleholm C",
    "740001582":"Hörnefors station",
    "740001560":"Iggesund",
    "740000202":"Insjön",
    "740000126":"Järpen",
    "740000146":"Järvsö",
    "740000090":"Jönköping C",
    "740000282":"Jörn",
    "740000326":"Kaitum",
    "740000020":"Kalmar C",
    "740000903":"Karbenning",
    "740000070":"Karlstad C",
    "740000166":"Katrineholm C",
    "760002405":"Katterat",
    "740001432":"Katterjåkk",
    "740000345":"Kilafors",
    "740001602":"Kiruna station",
    "740000559":"Knivsta station",
    "740000321":"Kolbäck",
    "740001545":"Kolmården station",
    "760000318":"Kongsvinger",
    "740000280":"Kopparberg",
    "740000220":"Kramfors station",
    "740000222":"Kristinehamn",
    "740000228":"Krokom",
    "740000192":"Kumla",
    "740000161":"Kungsbacka",
    "740000676":"Kungsör station",
    "740000677":"Kvicksund station",
    "740000945":"Kävlinge",
    "860000626":"Köbenhavn H",
    "860000650":"Köbenhavn Österport",
    "740000167":"Köping station",
    "740000554":"Landvetter centrum",
    "740000194":"Laxå station",
    "740000019":"Leksand",
    "740000540":"Lerum",
    "740000235":"Lessebo",
    "760000207":"Lilleström",
    "740000100":"Limmared",
    "740000093":"Lindesberg",
    "740000635":"Lingbo",
    "740000009":"Linköping C",
    "740000245":"Ljung",
    "740000325":"Ljungaverk",
    "740000198":"Ljusdal",
    "740001559":"Ljusne station",
    "740000291":"Ludvika station",
    "740000144":"Luleå C",
    "740002953":"Notviken station",
    "740000120":"Lund C",
    "740000360":"Lycksele station",
    "740000206":"Lysekil station",
    "740001433":"Låktatjåkka",
    "740000067":"Läggesta",
    "740001591":"Lödöse Södra station",
    "740000003":"Malmö C",
    "760001124":"Marienborg TND",
    "740000039":"Mellerud",
    "740000180":"Mjölby",
    "740000302":"Mora station",
    "740020170":"Morastrand station",
    "740000736":"Morgongåva",
    "760000516":"Moss",
    "740000172":"Motala",
    "740000087":"Munkedal",
    "740000268":"Murjek",
    "740000027":"Märsta station",
    "740000153":"Mörsil station",
    "760002402":"Narvik stn",
    "740000265":"Nattavaara",
    "740001583":"Nordmaling station",
    "740000007":"Norrköping C",
    "740000189":"Nybro",
    "740000816":"Nykroppa station",
    "740000149":"Nykvarn",
    "740000050":"Nyköping C",
    "740000140":"Nässjö C",
    "740000277":"Ockelbo",
    "740000295":"Osby",
    "760000220":"Oslo Lufthavn Gardermoen",
    "760000100":"Oslo S",
    "740000653":"Pilgrimstad",
    "740000046":"Ramnäs",
    "740000679":"Ransta",
    "740000229":"Riksgränsen",
    "760002404":"Rombak",
    "760000518":"Rygge",
    "740000158":"Rättvik",
    "740000214":"Sala",
    "740000195":"Sandviken station",
    "760000527":"Sarpsborg",
    "740001437":"Sjisjka",
    "740000075":"Skee",
    "760000508":"Ski",
    "740000186":"Skinnskatteberg",
    "740000545":"Skänninge station",
    "740000008":"Skövde C",
    "740000062":"Smedjebacken",
    "740000686":"Stavre station",
    "740000924":"Stenstorp",
    "740000001":"Stockholm Central",
    "740000622":"Sthlm Cityterm",
    "740000765":"Stockholm Södra",
    "740000347":"Storfors station",
    "740000025":"Storlien",
    "740000244":"Storvik",
    "740001567":"Storå station",
    "740000108":"Strängnäs",
    "740000095":"Strömstad",
    "740000638":"Ställdalen",
    "740000380":"Stöde",
    "740000773":"Sundbyberg station",
    "740022983":"Sunderby sjukhus station",
    "740000130":"Sundsvall C",
    "740020045":"Sundsvall Västra",
    "740000384":"Surahammar",
    "740000023":"Säffle",
    "740000026":"Säter",
    "740000024":"Söderbärke",
    "740000154":"Söderhamn station",
    "740000055":"Södertälje Syd",
    "760090014":"Sösterbekk",
    "740000233":"Tanum",
    "740000301":"Tierp station",
    "740000242":"Timrå station",
    "740000688":"Torpshammar station",
    "740001563":"Torsåker station",
    "740000041":"Tranås",
    "740000191":"Trollhättan C",
    "740001609":"Tvärålund station",
    "740000097":"Tällberg",
    "740000183":"Töreboda",
    "740000119":"Uddevalla C",
    "740000190":"Umeå C",
    "740001581":"Umeå Östra",
    "740000142":"Undersåker",
    "740000005":"Uppsala C",
    "740000683":"Vad station",
    "740000605":"Vagnhärad",
    "740000753":"Vallsta station",
    "740000016":"Vara station",
    "740000110":"Varberg",
    "740000012":"Vargön",
    "740000208":"Vassijaure",
    "740000386":"Vedum",
    "740000239":"Vindeln",
    "740000839":"Vingåker",
    "740000196":"Virsbo",
    "740000569":"Vårgårda station",
    "740000241":"Vänersborg C",
    "740000181":"Vännäs",
    "740013770":"Vännäsby station",
    "740000052":"Värnamo",
    "740001589":"Västeraspby station",
    "740000099":"Västerås C",
    "740000250":"Växjö station",
    "740000076":"Åmål",
    "740000105":"Ånge",
    "740000037":"Ånn",
    "740000115":"Åre",
    "740000045":"Älmhult",
    "740000156":"Älvsbyn",
    "740000789":"Älvsjö",
    "740000135":"Ängelsberg",
    "740000133":"Örebro C",
    "740000361":"Örebro Södra",
    "740001570":"Örnsköldsvik C",
    "740001569":"Örnsköldsvik Norra station",
    "740000123":"Östersund C",
    "740020168":"Östersund Västra station",
    "740000173":"Öxnered"
}

stops = sqlite3.connect('../static_data/stops')

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

    cookies = {
        "JSESSIONID":"RFTgxEOrdceORqH1aiKNy1ElGdb0KWN1JdqBChI9.258ba32350e6",
        "JSESSIONID":"CWLudVSaNo3EvqJAS9eqV727_24idFRc4i_vBn8Z.258ba32350e6"
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
      "travelDate": search["temporal"]["earliestDepature"][:-1]+".000Z",
      "travelDateAsString": search["temporal"]["earliestDepature"][0:10] + " " + search["temporal"]["earliestDepature"][11:19],
      "maxNumberOfChanges": "7"
    }

    result = requests.post(
        "https://www.norrtag.se/will/api/rest/timetable/searchTimetable",
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
        "https://www.norrtag.se/will/api/rest/gts/getPrice",
        data=json.dumps(price),
        headers=headers,
        cookies=cookies
        )

    url = "https://www.norrtag.se/#/"
    url = url + urllib.quote(urllib.quote(StopIdToName(search["route"][0]["stopId"]).encode('utf-8'))) + "/"
    url = url + urllib.quote(urllib.quote(StopIdToName(search["route"][1]["stopId"]).encode('utf-8'))) + "/enkel/avgang/"
    url = url + search["temporal"]["earliestDepature"].replace("-","").replace("T","-").replace(":","")[0:13] + "/avgang/"
    url = url + search["temporal"]["earliestDepature"].replace("-","").replace("T","-").replace(":","")[0:13]+"/VU--///0//"
    products = []
	
    for p in result.json():
      pricelist = []
      for price in p["salesCategories"]:
        pris = float(price["totalPrice"]["value"])
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

run(host='127.0.0.1', port=8087, reloader=True)