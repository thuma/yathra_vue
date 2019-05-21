# !/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, sqlite3, urllib

#sjstops = ["740000325","740000694","740000688","740000075","740000172","740000067","740000250","740000540","740000189","740020045","740000903","740000241","740000135","740000151","740000303","740000660","740000704","740000018","740000559","740001570","740000109","740000195","740000006","740000096","740000002","860000858","740000089","740000019","740001567","760000516","740000653","740000052","740000093"

#sjstops = ["740000254","740000245","740000632","740000183","740000324","740000025","740000003","740000789","740000190","740000300","740000679","740000736","740000149","760000508","740000144","740000482","740000384","740000105","740000677","740000110","740000569","740000042","740000062","740000077","740000196","760000522","740000378","740000180","740000012","740000218","740001582","740001437","760090014","760000100","740000221","740000076","740000414","760002402","740000192","740000242","740000143","740000291","760001122","740000282","740000099","740000217","740000108","740000265","740000065","740000023","740000032","740001602","740000239",

#sjstops = ["760000207","740000676","740000288","740000674","740000294","740000620","740000187","740000816","740001609","740000166","740020094","740000181","740000635","760000527","740000114","740001579","740001333","740000206","740000738","740000126","740000380","760000518","740000360","740000063","740000924","740000040","740000326","740000554","740000214","740000198","740000095","740000630","740000140","740000322","740000602","740000046","740000202","740000041","740012949","740000090","740000219","740000229","740000386","740001583","740001581","760000318","740000036","740021552","740001432","740000361","740000235","740000839","740000133","740000228","740000115","760000220","740000220","740000295","740000673","740000186","740000156","740000020","740000154","740000120","740001591","740000016","740020168","740000111","740000277","740001433","740000280","740001559","740000005","740000087","740000419","740000301","740001563","740000222","740000097","740000009","740000162","740000123","740000208","740000233","740000615","740000173","740000686","740001589","740000526","740000112","740000545","740000321","740000027","740000146","740000842","740000050","740000194","740000244","740000004","740000008","740000556","740000055","740000605","740000511","740000045","740000060","740000622","740000160","740000031","740022983","760002406","740000253","740000059","740001584","740001560","740020170","740000753","740000170","740000266","740000945","740000308","740000128","740000765","740000210","860000626","740013770","740000150","740000167","740000100","740000302","740000153","740000158","740000142","740000638","760001124","740000044","740000683","740000039","740000262","740000129","740000345","740000007","740000107","760000546","740001569","740000026","740000072","740000268","740000030","740000293","740001568","740000130",

#
sjstops = ["760002405","860000650","740000161","740000119","740000191","740000347","740000024","760002404","740000283","760000519","740000773","740002953","740000070","740000001","740000037","740000080","740001545"]
stops = sqlite3.connect('stops')

def StopIdToName(id):
  for row in stops.execute("SELECT stop_name FROM stops WHERE stop_id = %s" % id):
   return row[0]


for stop in sjstops:
  name = StopIdToName(stop)
  name = name.split("/")[0].encode("utf-8").replace("ø","ö").replace("Ø","Ö").replace("kk","k")
  stations = requests.get("https://www.tagbokningen.se/will/api/rest/location/normal/"+urllib.quote(name)+"/limitresult/1")
  if len(stations.json()) == 0:
    print stop + "," + requests.get("https://www.tagbokningen.se/will/api/rest/location/normal/"+urllib.quote(name.split(" ")[0])+"/limitresult/1").json()[0]
  else:
    print stop + "," + stations.json()[0]


 