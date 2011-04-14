import random
import socket
import time
import sys
from ahoy.agent import Agent
from ahoy.message import Message
from ahoy.util.aisdatagen import AISDataGen


class AISShip(Agent) :
    def __init__(self, uid, forward_vel, port) :
        Agent.__init__(self, uid)
        self._forward_vel = forward_vel
        self._agl = 0.002 
        self._vert_vel = 0
        self._port = port 
        self._use_ais = True
        self._man_paths = []     
        
    def run(self) :
        self.get_owner_node().get_interface('wlan0').set_recv_callback(self._changedata) 
        self._path_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._path_conn.connect(('', self._port))
        uid = self.get_owner_node().get_uid()
        #olat, olon, oagl = self.get_owner_node().get_position()
        self._path_conn.send("INIT")
        orig_pos = self._path_conn.recv(1024)
        self._lat, self._lon = orig_pos.split(',')
        self.get_owner_node().set_position(float(self._lat),float(self._lon),self._agl)
        
        while True:
            posdata = (self._lat) + "," + (self._lon)
            newpos = ""
            if self._use_ais:
                print str(uid) + " sending " + posdata
                self._path_conn.send(posdata)
                newpos = self._path_conn.recv(1024)
                print str(uid) + " received " + newpos
            else:
                #TODO: What happens when the path is done? 
                newpos = self._man_paths.pop(0)    
            self._move(newpos) 
            self._publishmove() 
            time.sleep(1)

    #  Changes the path data for the ais ship based on whats sent in
    #  the event. WARNING: The format of the message is tbd
    def _changedata(self, event):
        print "CHANGING DATA"
        self._use_ais = False
        newpaths = event.get_message().get_payload()
        self._man_paths = newpaths.split(';')

    def _move(self, posdata):
        lat, lon = posdata.split(',')
        self._lat = lat
        self._lon = lon
        self.get_owner_node().move(float(self._lat), float(self._lon), self._agl, self._forward_vel, self._vert_vel, True)

    def _publishmove(self):
        uid = self.get_uid()
        message = str(uid) + "," + self._lat + "," + self._lon + "," + str(self._agl) + "," + str(self._forward_vel)
        self.get_owner_node().get_interface("wlan0").send(message, uid)

#if __name__ == '__main__':
#    lat = "39.881592"
#    lon = "-75.172737"
#    port = int(sys.argv[1])
#    ship = AISShip(lat,lon,port)
#    ship.run()
