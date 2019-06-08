# !/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3

stops = {
"740000008":"",
"740000031":"",
"740000041":"",
"740000044":"1170",
"740000055":"",
"740000060":"",
"740000067":"",
"740000070":"",
"740000084":"",
"740000086":"",
"740000090":"1207",
"740000094":"",
"740000099":"1157",
"740000120":"1171",
"740000124":"",
"740000133":"1223",
"740000140":"",
"740000148":"",
"740000167":"",
"740000170":"",
"740000172":"",
"740000176":"",
"740000180":"1186",
"740000216":"",
"740000222":"1160",
"740000231":"",
"740000250":"1530",
"740000256":"",
"740000266":"1182",
"740000291":"",
"740000300":"1218",
"740000364":"1543",
"740000373":"",
"740000554":"1181",
"740000611":"",
"740000622":"1155",
"740000648":"",
"740000862":"",
"740001452":"",
"740004066":"",
"740004265":"",
"740010450":"",
"740010760":"",
"740010955":"1187",
"740011102":"",
"740011131":"1188",
"740011151":"1147",
"740011369":"",
"740011547":"",
"740012949":"1181",
"740014463":"1531",
"740016443":"",
"740020261":"",
"740020483":"1164",
"740020671":"1156",
"740020821":"",
"740021191":"",
"740022989":"",
"740023098":"1163",
"740023202":"",
"740023224":"",
"740023227":"",
"740023566":"",
"740023572":"",
"740023573":"",
"740023894":"",
"740024007":"",
"740024011":"",
"740024017":"",
"740024046":"",
"740024369":"",
"740024999":"1551",
"740033206":"1156",
"740037442":"",
"740043310":"",
"740045190":"",
"740049383":"",
"740059127":"",
"740061760":"",
"740062068":"",
"740072050":"1172",
"740072204":"",
"740072206":"",
"740072207":"",
"740074626":"1225",
"760025036":"556",
"760090001":"720",
"760090003":"",
"760090017":"",
"860000858":"",
"860024917":""
}

nbdata = """Arboga,5649,Arboga Sätra Dinners/Ingo,1225
Arendal,5566,Harebakken bussterminal,324
Arendal,5566,Nedeneskrysset,664
Arlanda,5611,Arlanda flygplats,1156
Asker,5565,Hagaløkka,314
Aurland,5526,Aurland,28
Aurland,5526,Flåm stasjon,220
Aurland,5526,Gudvangen E16,301
Bærum,5760,Høvik/Ramstadsletta,1525
Bærum,5760,Lysaker stasjon,594
Bærum,5760,Sandvika bussterminal,796
Bamble,5569,Rugtvedt E18,763
Bergen,5544,Arna terminal,16
Bergen,5544,Bergen busstasjon,50
Bergen,5544,Åsane terminal,1120
Borås,5626,Borås Resecentrum hpl P,1218
Drammen,5509,Bangeløkka,42
Drammen,5509,Brakerøya,93
Drammen,5509,Tinghuset,1149
Drammen,5509,Torget Vest,980
Drammen,5509,Vårveien,1078
Drammen,5509,Åssiden vgs.,1132
Eid,5534,Hjelle kryss Eid,376
Eid,5534,Lote ferjekai,1296
Eid,5534,Nordfjordeid rutebilstasjon,682
Eid,5534,Stårheim ferjekai,919
Eidsvoll,5524,Byrud,121
Eidsvoll,5524,Feiring Samvirkelag,201
Eidsvoll,5524,Minnesund industriområde,632
Eidsvoll,5524,Nebbenes E6,663
Eidsvoll,5524,Stubberud,915
Eke,5686,Eke Terminalen,1531
Elverum,5591,Elverum skysstasjon,178
Fagersta,5633,Fagersta,1182
Flora,5658,Florø rutebilstasjon,1237
Flå,5539,Flå sentrum,219
Flå,5539,Gulsvik Circle K,302
Fredrikstad,5555,Fredrikstad bussterminal,238
Fredrikstad,5555,Kjøkøy,467
Fredrikstad,5555,Møllerodden,654
Fredrikstad,5555,Skårakrysset,851
Fredrikstad,5555,Ørebekk rv. 110,1089
Førde,5550,Førde rutebilstasjon,258
Førde,5550,Moskog,645
Gardermoen,5735,Oslo lufthavn,721
Gaular,5666,Sande,1289
Gaular,5666,Storehaug,1288
Geilo,5733,Geilo stasjon,268
Gjerstad,5598,Brokelandsheia E18,105
Gjøvik,5558,Bondelia,82
Gjøvik,5558,Gjøvik Skysstasjon,276
Gjøvik,5558,Mjøsbrua vest,634
Gloppen,5653,Anda ferjekai,1294
Gloppen,5653,Byrkjelo,1290
Gloppen,5653,Sandane rutebilstasjon,1292
Gol,5584,Gol skysstasjon,279
Grimstad,5590,Øygårdsdalen,1102
Gulen,5606,Instefjord,434
Gulen,5606,Oppedal ferjekai,713
Göteborg,5619,Göteborg Nils Ericssons Terminal,1164
Helsingborg,5625,Helsingborg (Knutpunkten),1170
Hemsedal,5535,Bjøberg,65
Hemsedal,5535,Hemsedal sentrum,360
Hemsedal,5535,Tuv,1012
Hemsedal,5535,Ulsåk,1020
Hol,5518,Hagafoss,312
Hole,5563,Sollihøgda,876
Hole,5563,Sundvollen,924
Hornindal,5567,Grodås,292
Hornindal,5567,Kjøs bru,472
Horten,5575,Kopstadkrysset,495
Hvaler,5548,Bratte Bakke,96
Hvaler,5548,Skjærhalden,836
Høyanger,5595,Lavik kai,549
Høyanger,5595,Vadheim,1023
Jevnaker,5573,Jevnaker rutebilstasjon,440
Jølster,5593,Skei i Jølster,822
Jølster,5593,Vassenden Jølster,1036
Jølster,5593,Ålhus,1108
Jönköping,5629,Jönköping Resecentrum,1207
Karlskoga,5637,Karlskoga Busstation,1159
Karlstad,5616,Karlstad Busstation,1161
Karlstad,5616,Karlstad Centralstation,1173
Kastrup,5623,Kastrup Terminal 3,1168
Knöstad,5736,Knöstad Bytespunkt, Nysäter E18,1551
Kongsberg,5580,Kongsberg knutepunkt,491
Kongsberg,5580,Kongsbergtoppen,493
Kongsberg,5580,Meheia,620
Kongsberg,5580,Saggrenda,776
Kongsberg,5580,Teknologiparken,961
Kragerø,5562,Kragerø rutebilstasjon,1336
Kristiansand S,5523,Kristiansand rutebilstasjon,501
Kristiansund N,5515,Kristiansund trafikkterminal,502
Kristinehamn,5615,Kristinehamn Resecentrum,1160
Krødsherad,5551,Hamremoen kryss,320
Krødsherad,5551,Krøderen,506
Krødsherad,5551,Noresund,687
Krødsherad,5551,Ørgenvika,1090
Köpenhamn,5624,Köpenhamn Ingerslevsgade vid DGI-byn,1169
Lærdal,5538,Borlaug,88
Lærdal,5538,Fodnes ferjekai,221
Lærdal,5538,Håbakken,423
Lærdal,5538,Lærdal rådhus,597
Landvetter Flygplats,5634,Landvetter Flygplats,1184
Larvik,5605,Ringdalkrysset,752
Lillehammer,5528,Lillehammer skysstasjon,560
Lillesand,5582,Gaupemyr bussterminal,265
Lindås,5587,Knarvik skysstasjon,486
Lindås,5587,Romarheim kryss E39,759
Linköping,5628,Linköping (Fjärrbussterminalen),1187
Lom,5557,Lom,579
Ludvika,5630,Ludvika,1179
Lund,5621,Lund Järnvägsstation Hpl H,1171
Løten,5519,Myklegard,652
Løten,5519,Segla bru,804
Malmö,5622,Malmö Norra Vallgatan Läge K,1172
Malvik,5537,Leistadkrysset,555
Masfjorden,5588,Matre,616
Mjölby,5635,Mjölby Resecentrum,1186
Modum,5529,Vikersund Rv 280/35,1055
Modum,5529,Åmot Skillebekk,1112
Molde,5536,Molde trafikkterminal,641
Moss,5514,Høyden Ryggeveien,420
Moss,5514,Mosseporten,646
Moss,5514,Nesparken,671
Nedre Eiker,5543,Mjøndalen E134,633
Nes(Buskerud),5589,Bromma,106
Nes(Buskerud),5589,Nesbyen Shell,669
Nord-Fron,5530,Kvam E6,516
Nord-Fron,5530,Vinstra vegpark,1063
Norrköping,5636,Norrköping (Resecentrum),1188
Notodden,5511,Notodden skysstasjon,691
Notodden,5511,Ørvella fv. 361,1389
Nyköping,5731,Nyköping,1547
Oslo,5559,Oslo bussterminal,720
Porsgrunn,5604,Skjelsvik terminal,830
Rena,5684,Rena skysstasjon,1527
Ringebu,5577,Ringebu skysstasjon,753
Ringerike,5525,Hønefoss sentrum,417
Ringerike,5525,Sokna,871
Ringsaker,5594,Nydal Circle K,695
Risør,5572,Vinterkjær,1064
Rygge,5542,Halmstad,316
Rygge,5542,Rygge E6,764
Råde,5552,Jonsten E6,1483
Råde,5552,Karlshus Esso,451
Sandefjord,5600,Fokserød,222
Sarpsborg,5554,Lekevollkrysset E6,556
Sarpsborg,5554,Sarpsborg bussterminal,798
Sarpsborg,5554,Sykehuset Østfold Kalnes,938
Sel,5734,Otta Circle K,724
Sel,5734,Otta skysstasjon,725
Skedsmo,5533,Olavsgaard,708
Skjåk,5570,Grotli,293
Skjåk,5570,Langvatn Skjåk,543
Smedjebacken,5631,Smedjebacken (OKQ8),1180
Sogndal,5531,Fjærland kryss,212
Sogndal,5531,Kaupangsenteret,455
Sogndal,5531,Mannheller ferjekai,611
Sogndal,5531,Selseng bru,807
Sogndal,5531,Sogndal skysstasjon,868
Stange,5546,Espa E6,192
Stange,5546,Romedal rv. 3,760
Stockholm,5610,Stockholm Cityterminalen,1155
Stryn,5571,Stryn rutebilstasjon,911
Sula,5667,Solavågen ferjekai,1302
Sunndal,5574,Sunndalsøra,925
Surnadal,5513,Skei Surnadal,928
Söderbärke,5632,Söderbärke Busstationen,1181
Sør-Fron,5540,Harpefoss E6,326
Tanum,5617,Tanum Preem,1162
Tinn,5674,Mæl rasteplass,1377
Tinn,5674,Rjukan rutebilstasjon,1338
Trondheim,5553,Prinsen Kinosenter,732
Trondheim,5553,Studentersamfundet,917
Trondheim,5553,Trondheim S,1000
Tønsberg,5581,Sem E18 (Aulerød),811
Uddevalla,5618,Uddevalla Torp Hållplatsläge F,1163
Ullensaker,5609,Gardermoen Næringspark,262
Ullensaker,5609,Lokevegen (LHL),1234
Ullensaker,5609,Skibakk,827
Ulstein,5561,Ulsteinvik skysstasjon,1019
Værnes,5576,Trondheim lufthavn,999
Vaksdal,5597,Dale sentrum,131
Vaksdal,5597,Vaksdal E16,1024
Vestby,5683,Sonsveien stasjon,1484
Vestby,5682,Vestby bru,1482
Volda,5516,Furene,247
Volda,5516,Geitvik,701
Volda,5516,Langvatn E39,544
Volda,5516,Volda rutebilstasjon,1065
Voss,5545,Bolstad,81
Voss,5545,Evanger E16,194
Voss,5545,Vinje,1058
Voss,5545,Voss stasjon,1072
Vågsøy,5541,Allmenningsfjellet,7
Vågsøy,5541,Bryggja,618
Vågsøy,5541,Måløy terminal,657
Vågsøy,5541,Torghopen Måløy kai,981
Vågå,5560,Vågåmo Smedsmo,1077
Västerås,5612,Västerås Resecentrum,1157
Växjö,5685,Växjö Busstation,1530
Ål,5510,Lienkrysset,982
Ål,5510,Ål sentrum,1107
Ålesund,5660,Campus Ålesund,1246
Ålesund,5660,Moa trafikkterminal,1248
Ålesund,5660,Ålesund rutebilstasjon,1245
Årdal,5675,Årdalstangen sentrum,1415
Årdal,5675,Øvre Årdal skysstasjon,1413
Årjäng,5695,Årjäng Busstation,1543
Ås,5596,Korsegården,498
Örebro,5613,Örebro Resecentrum,1223
Ørsta,5522,Festøya ferjekai,1301
Ørsta,5522,Liadal,1299
Ørsta,5522,Vartdal,1300
Ørsta,5522,Ørsta rutebilstasjon,1094
Østre Toten,5564,Bilitt,58
Østre Toten,5564,Fjellhaug,210
Østre Toten,5564,Lena skysstasjon,559
Østre Toten,5564,Nordlia handel,684
Østre Toten,5564,Skreia,842
Øvre Eiker,5579,Dunserud E134 Darbu,154
Øvre Eiker,5579,Hokksund Langebru,381
Øvre Eiker,5579,Lerbergkrysset,382
Øyer,5578,Tretten E6 (Holmen bru),997
Øyer,5578,Øyer sentrum,1100""".split("\n")

def find():
  stopsdb = sqlite3.connect('../static_data/stops')
  for id in stops:
    for row in stopsdb.execute("SELECT stop_name FROM stops WHERE stop_id = %s" % id):
      found = False
      for nb in nbdata:
        if row[0].encode("utf-8")[0:4] in nb:
          print id+","+row[0].encode("utf-8")+","+nb
          found = True;
      if not found:
        print id + row[0]