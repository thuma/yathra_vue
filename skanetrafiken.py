# -*- coding: utf-8 -*-
#!/usr/bin/python
"""WSGI server example"""
from gevent.pywsgi import WSGIServer
import requests
import xmltodict
import json

def getIdFor(x,y):
    url = "http://www.labs.skanetrafiken.se/v2.2/neareststation.asp"
    params = {
        "x":x,
        "y":y,
        "Radius":"500"
    }
    result = requests.get( url, params = params)
    xmlstring = xmltodict.parse(result.content)
    return xmlstring["soap:Envelope"]["soap:Body"]["GetNearestStopAreaResponse"]["GetNearestStopAreaResult"]["NearestStopAreas"]["NearestStopArea"][0]

def getPrice(fromid,toid,time):
    url = "http://www.labs.skanetrafiken.se/v2.2/resultspage.asp"
    params = {
        "cmdaction":"search",
        "selPointFr":"F|"+fromid+"|0",
        "selPointTo":"T|"+toid+"|0",
        "inpTime":time[11:16],
	    "inpDate":time[0:10]
    }
    result = requests.get( url, params = params)
    xmlstring = xmltodict.parse(result.content)
    return xmlstring["soap:Envelope"]["soap:Body"]

def application(env, start_response):
    if env['PATH_INFO'] == '/':
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [b"<b>hello world</b>"]
    else:
        start_response('404 Not Found', [('Content-Type', 'text/html')])
        return [b'<h1>Not Found</h1>']

if __name__ == '__main__':
    print('Serving on 8088...')
    WSGIServer(('127.0.0.1', 8088), application).serve_forever()
