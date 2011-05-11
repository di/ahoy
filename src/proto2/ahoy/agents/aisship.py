import random
import socket
import time
import sys
from ahoy.agent import Agent
from ahoy.message import Message
from ahoy.util.aisdatagen import AISDataGen
from ahoy.util.geo import *
from threading import Thread

class AISShip(Agent) :
    def __init__(self, uid, forward_vel, ip, port, iface_name):
        Agent.__init__(self, uid)
        self._forward_vel = forward_vel
        self._agl = 0.002 
        self._vert_vel = 0
        self._port = port # The port it communicates to the AISDataGen with 
        self._use_ais = True  #if True, uses AISDataGen info to move
        self._iface_name = iface_name  #interface on the node it communicates ais info through
        self._man_paths = []     #list of paths to follow given by human operator
        self._ip = ip 
        self._last_lat = None
        self._NtoS = False

    def run(self) :
        #sets the callback to listen for divert events
        self.get_owner_node().get_interface(self._iface_name).set_recv_callback(self._changedata) 
        self._path_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._path_conn.connect((self._ip, self._port))
        uid = self.get_owner_node().get_uid()
        # Gets a random initial position from AISDataGen
        self._path_conn.send("INIT")
        orig_pos = self._path_conn.recv(1024)
        self._lat, self._lon = orig_pos.split(',')
        self.get_owner_node().set_position(float(self._lat),float(self._lon),self._agl)
        Thread(target=self._publishlocation).start() 
        
        while True:
            posdata = (self._lat) + "," + (self._lon)
            newpos = ""
            if self._use_ais:
                path_dist = self._distToPath()
                if(path_dist != None and path_dist <= 0.4):
                    self._use_ais = False
                    newpos = self._man_paths.pop(0)
                else:
                    self._path_conn.send(posdata)
                    newpos = self._path_conn.recv(1024)
            else:
                #TODO: What happens when the path is done?
                if(len(self._man_paths) > 0): 
                    newpos = self._man_paths.pop(0)  
                else:
                    self._use_ais = True  
            self._move(newpos) 
            #self._publishmove() 
            time.sleep(1)

    #  Changes the path data for the ais ship based on whats sent in
    #  the event. WARNING: The format of the message is tbd
    def _changedata(self, event, iface=None):
        payload = event.get_message().get_payload()
        if(event.get_src_agent_uid() != self.get_uid() and payload.startswith("DIVERT")):
            print "CHANGING DATA"
            #print str(event.get_src_agent_uid()) + " = " + str(self.get_uid())
            newpaths = payload
            paths = newpaths.split(';')
            paths = paths[1:]
            closest = []
            min_index = 0
            mylat = float(self._lat)
            mylon = float(self._lon)
            last_lat = None
            NS = False
            # Find the closest point in the path and determine the direction
            # of the path
            for i in range(0,len(paths)):
                lat,lon = map(float, paths[i].split(','))
                #lat = float(lat)
                #lon = float(lon)
                if(len(closest) == 0 or lin_distance(lat,lon,0,mylat,mylon,0) < closest):
                    min_index = i
                    closest = [lat,lon]
                if(last_lat != None and lat < last_lat):
                    NS = True
                last_lat = lat

            # figure out the direction to take
            above = False
            if(closest[0] < mylat):
                above = True
            #Return if moving away from path
            if(((not above) and self._NtoS) or ( above and (not self._NtoS))):
                self._use_ais = True
                return 
            #Reverse the path if your are moving in the opposite
            #direction than they were created in
            if((not above) and NS and (not self._NtoS)):
                paths = [x for x in reversed(paths)]
                i = (len(paths)-1)-i
            elif(above and (not NS) and self._NtoS):
                paths = [x for x in reversed(paths)]
                i = (len(paths)-1)-i

            self._man_paths = paths[i:]
            
    def _move(self, posdata):
        lat, lon = posdata.split(',')
        self._lat = lat
        self._lon = lon
        if(self._last_lat != None):
            if(float(lat) < self._last_lat):
                self._NtoS = True
        self._last_lat = float(lat)
        self.get_owner_node().move(float(self._lat), float(self._lon), self._agl, self._forward_vel, self._vert_vel, True)

    #publishes its own AIS position 
    def _publishmove(self):
        uid = self.get_uid()
        message = str(uid) + "," + self._lat + "," + self._lon + "," + str(self._agl) + "," + str(self._forward_vel)
        m = Message(message,'*')
        self.get_owner_node().get_interface(self._iface_name).send(m, uid)

    def _publishlocation(self):
        while True:
            loc = self.get_owner_node().get_position()
            uid = self.get_uid()
            message = str(uid) + "," + str(loc[0])  + "," + str(loc[1]) + "," + str(self._agl) + "," + str(self._forward_vel)
            print "Publishing: " + message
            m = Message(message, '*')
            self.get_owner_node().get_interface(self._iface_name).send(m,uid)
            time.sleep(1)

    def _distToPath(self):
        if(len(self._man_paths) > 0):
            mylat = float(self._lat)
            mylon = float(self._lon)
            lat,lon = map(float, self._man_paths[0].split(','))
            return lin_distance(mylat,mylon,0,lat,lon,0)
        else:
            return None
#if __name__ == '__main__':
#    lat = "39.881592"
#    lon = "-75.172737"
#    port = int(sys.argv[1])
#    ship = AISShip(lat,lon,port)
#    ship.run()
