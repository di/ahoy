import random
from random import choice
import sys
import socket
import time
from threading import Thread

class AISDataGen():
    def __init__(self, hostname, port, data=None):
     
        self.probs_ = {}
        if(data == None or data == ""):   
            self.file_ = "AIS_trimmed.dat"
        else:
            self.file_ = data
        
        self._tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._tcp_server.bind((hostname, port))
        self._tcp_server.listen(1)

    def start(self) :
        t = Thread(target=self._acceptor)
        t.start()
        return t

    def _acceptor(self) :
        while True :
            conn, addr = self._tcp_server.accept()
            #self._clients.add(conn)
            Thread(target=self._listener, args=(conn,)).start()

    def _listener(self, conn) :
        while True:
            data = conn.recv(1024)
            if(data == "INIT"):
                conn.send(self.get_rand_location())
            else:
                #print "RECEIVED: " + data
                try:
                    lat,lon = data.split(',')
                    lat,lon = self.get_next_location(lat,lon)
                    conn.send(lat+","+lon)
                except:
                    print "AISDatagen getting bad connection. Closing listener"
                    break

        conn.close()

    #Reads in the values to the probs dict
    def initialize(self):
        print "Initializing..."
        file = open(self.file_,'r')
        for line in file:
            line = line.rstrip('\n')
            data = line.split(':')
            self._addTransition(data)
        print "Done initializing."

    #adds a transition to the probs dict
    #data is a list of lat,lon,and probability of reaching 
    #that state. 
    def _addTransition(self, data):
        if(not (self.probs_.has_key(data[0]))):
            self.probs_[data[0]] = {}
        self.probs_[data[0]][data[1]] = float(data[2])



    def get_rand_location(self):
        return choice(self.probs_.keys())
    
    def get_next_location(self, latfrom, lonfrom):
        #key = str(latfrom) + "," + str(lonfrom)
        key = latfrom + "," + lonfrom
        if(not self.probs_.has_key(key)):
            return [latfrom, lonfrom]

        else:
            to_loc = self.probs_[key].keys()
            rand = random.random()
            n = 0
            #only going to len(to_loc)-1 so that we can avoid the 
            #probabilities not adding up to 1 and getting 1 as our
            #random number
            for i in range(0,len(to_loc)-1):
                chance = self.probs_[key][to_loc[i]]
                n = n + chance
                if(n <= rand):
                    lat, lon = to_loc[i].split(',')
                    #return [float(lat),float(lon)]
                    return [lat,lon]

            #if we made it this far we know its the last location
            #that we need. 
            lat,lon = to_loc[len(to_loc)-1].split(',')
            #return [float(lat),float(lon)]
            return [lat,lon]

if __name__ == '__main__' :
    if len(sys.argv) < 3 :
        print 'usage: python aisdatagen.py <hostname> <port> <filepath>'
        sys.exit(0)
    host = sys.argv[1]
    port = int(sys.argv[2])
    filepath = ""
    if(len(sys.argv) >= 4):
        filepath = sys.argv[3]
    datagen = AISDataGen(host, port, filepath)
    datagen.initialize()
    print 'Starting datagen on', port
    datagen.start().join()
