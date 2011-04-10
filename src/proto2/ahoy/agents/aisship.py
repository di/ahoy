import random
import socket
import time
import sys
from ahoy.agent import Agent
from ahoy.message import Message
from ahoy.util.aisdatagen import AISDataGen


class AISShip(Agent) :
    def __init__(self, owner_node, forward_vel, port) :
        Agent.__init__(self, owner_node)
        self._forward_vel = forward_vel
        #self._lat = start_lat
        #self._lon = start_lon
        self._agl = 0.2; 
        self._vert_vel = 0; 
        #self._pathfile = pathfile
        
        self._path_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._path_conn.connect(('', port))


    def run(self) :
        print "==Running=="
        olat, olon = self.get_owner_node().get_position()
        self._lat = str(olat)
        self._lon = str(olon)
        while True:
            posdata = (self._lat) + "," + (self._lon)
            print "Sending " + posdata
            self._path_conn.send(posdata); 
            newpos = self._path_conn.recv(1024)
            print "Received " + newpos
            self._move(newpos)            
            time.sleep(5)


    def _move(self, posdata):
        lat, lon = posdata.split(',')
        self._lat = lat
        self._lon = lon
        self.get_owner_node().move(float(self._lat), float(self._lon), self._agl, self._forward_vel, self._vert_vel)

#if __name__ == '__main__':
#    lat = "39.881592"
#    lon = "-75.172737"
#    port = int(sys.argv[1])
#    ship = AISShip(lat,lon,port)
#    ship.run()
