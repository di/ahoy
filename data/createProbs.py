#!/usr/local/bin/python 

from datetime import datetime, date, time

        
id_file = "diffs.out"
data_file = "sorted.dat"

file = open(id_file,'r')
valid_ids = []

for line in file:
    info = line.split(' ')
    valid_ids.append(info[0])

file.close()

file = open(data_file, 'r')
pos_map = {} 
counts = {}
last_pos = ""
last_id = ""
linenum = 1
paths = []
currentPath = []
last_lat = ""
last_lon = ""
for line in file:
    line = line.rstrip('\n')
    info = line.split(',')
    id = info[4]
    lat = info[13]
    lon = info[14]
    if(valid_ids.count(id) > 0):
        if(last_lat == ""):
            pos_map[lat] = {}
            pos_map[lat][lon] = {}
            counts[lat] = {}
            counts[lat][lon] = 0.0
        else:
            if(not (pos_map.has_key(lat))):
                pos_map[lat] = {}
                counts[lat] = {}
            if(not (pos_map[lat].has_key(lon))):
                pos_map[lat][lon] = {}
                counts[lat][lon] = 0.0

            if(pos_map[last_lat][last_lon].has_key(lat)):
                if(pos_map[last_lat][last_lon][lat].has_key(lon)):
                    pos_map[last_lat][last_lon][lat][lon] = pos_map[last_lat][last_lon][lat][lon] + 1.0
                else:
                    pos_map[last_lat][last_lon][lat][lon] = 1.0
            else:
                pos_map[last_lat][last_lon][lat] = {}
                pos_map[last_lat][last_lon][lat][lon] = 1.0
          
            counts[last_lat][last_lon] = counts[last_lat][last_lon] + 1.0
    
        last_lat = lat
        last_lon = lon
    #if(linenum % 1000 == 0):
    #    print linenum
    #linenum = linenum + 1
file.close()

print "Starting to traverse the data ...\n"

file = open("probs/probs.out", 'w')
for fromlat in pos_map.keys():
    for fromlon in pos_map[fromlat].keys():
        for tolat in pos_map[fromlat][fromlon].keys():
            for tolon in pos_map[fromlat][fromlon][tolat].keys():
                num = pos_map[fromlat][fromlon][tolat][tolon]
                perc = num / counts[fromlat][fromlon]
                file.write(fromlat + "," + fromlon + ":" + tolat + "," + tolon + ":" + str(perc) + "\n")

file.close()

