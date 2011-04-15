# 
# Notes for now
# 
# AIS: ID, lat, lon, agl, speed
# Sonar, Radar: bearing, distance
#           call loc_from_baring_dist(lat, lon, bearing, distance)
#           bearing 0 north, 90 east, etc.

from ahoy.agent import Agent

class CorrelationAgent(Agent):
    
    def __init__(self, uid, threat_dist, ais_threshold, iface_s1, iface_s2, iface_r1, iface_ais) :
        Agent.__init__(self, uid)
        self._iface_s1 = iface_s1
        self._iface_s2 = iface_s2
        self._iface_r1 = iface_r1

        self._threat_dist = threat_dist
        self._ais_threshold = ais_threshold
        self._iface_ais = iface_ais
        
        self._correlation = {}
        self._sensor_data = {}
        self._ais_data = {}
    
    def run():
        self.get_owner_node().get_interface(self._iface_s1).set_recv_callback(self._s1_data)
        self.get_owner_node().get_interface(self._iface_s2).set_recv_callback(self._s2_data)
        self.get_owner_node().get_interface(self._iface_r1).set_recv_callback(self._r1_data)
        #self.get_owner_node().get_interface(self._iface_ais).set_recv_callback(self._ais_data)
        
    
    def _s1_data(self, event):
        # Got data from sonar 1
        # This method should not be getting called for now,
        # since sonars don't yet push that data this way.
        msg = event.get_message().get_payload()
        print 'someone is trying to be a sonar but isn\'t.'
        
    def _s2_data(self, event):
        msg = event.get_message().get_payload()
        #pass
    
    def _r1_data(self, event):
        msg = event.get_message().get_payload()
        #pass
    
    def _ais_data(self, event):
        msg = event.get_message().get_payload()
        s_id, lat, lon, agl, speed = msg.split(',')
        
        if s_id in self._ais_data.keys():
            if len(self._ais_data[s_id]) > self._ais_hist:
                self._ais_data[s_id].pop(0)
                self._ais_data.append([lat, lon, speed])    # ignoring agl
        
        #for key in self._ais_data.keys():
        #    a_lat, a_lon = self._ais_data[key][:2]
        #    if haver_dist(a_lat, a_lon, lat, lon) < 
        
    
        

'''
THREAT_MIN_D = 0.01 # in km
AIS_DATA = {}

def read_ais():
    i=0
    for l in 'ais_data':
        loc = [ float(s) for s in l.split() ]
        AIS_DATA[i] = loc
        i += 1

closest = {}

read_ais()

for sensor_pt in 'sensor_data':
    # make a random sensor point
    
'''


