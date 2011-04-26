# 
# Notes for now
# 
# AIS: ID, lat, lon, agl, speed
# Sonar, Radar: bearing, distance
#           call loc_from_baring_dist(lat, lon, bearing, distance)
#           bearing 0 north, 90 east, etc.

from ahoy.agent import Agent
from ahoy.util.geo import *

import time
from threading import Lock

from ahoy.eventapi import EventAPI
from ahoy.events.correlation import CorrelationEvent

class CorrelationAgent(Agent):
    
    def __init__(self, uid, threat_dist, ais_threshold, iface_s1, iface_s2, iface_r1, iface_ais) :
        Agent.__init__(self, uid)
        self._iface_s1 = iface_s1
        self._iface_s2 = iface_s2
        self._iface_r1 = iface_r1
        self._iface_ais = iface_ais
        
        # max distance from AIS data point to sensor data point, to consider a sensor data point a threat to AIS point
        self._threat_dist = threat_dist
        # max distance for an AIS and sensor point to be considered the same point
        # this may not actually get used yet
        self._ais_threshold = ais_threshold
        
        self._correlation = {}
        self._sensor_data = []
        self._ais_data = {}
        self._radar_data = {}   # keyed by bearing
        self._sonar1_data = {}  # keyed by bearing
        self._sonar2_data = {}  # keyed by bearing
        
        self._event_api = None
    
    def run(self):
        print 'Running correlation agent...'
        
        self._event_api = EventAPI()
        self._event_api.start()
        
        self.lock = Lock()
        
        self.get_owner_node().get_interface(self._iface_s1).set_recv_callback(self._new_sonar1_data)
        self.get_owner_node().get_interface(self._iface_s2).set_recv_callback(self._new_sonar2_data)
        self.get_owner_node().get_interface(self._iface_r1).set_recv_callback(self._new_radar1_data)
        self.get_owner_node().get_interface(self._iface_ais).set_recv_callback(self._new_ais_data)
        
        while True:
            
            '''recreate list of most recent sensor data, as it may have been updated'''
            # possibly move this action to functions where individual data points are added
            self._update_sensor_data()
            
            '''clear all correlations for now
                This way, there will be no chance of having an AIS ship point still correlated to an outdated
                sensor point (which may no longer even exist)'''
            self._correlation.clear()
            
            '''for each sensor data item ("current sensor item"), see which AIS data point is closest.
            If distance from the current sensor item is less than or equal to 
            the most recent smallest distance from a sensor point to this AIS data point,
            then set update the most recent smallest sensor point to be the current sensor item.'''
            #for ais_data in self._ais_data.keys():
            print 'About to update self._correlation...'
            for sensor_pt in self._sensor_data:
                print 'Correlating ', sensor_pt
                
                for ais_id in self._ais_data:
                    ais_pt = self._ais_data[ais_id]
                    
                    dist = haver_distance( sensor_pt[0], sensor_pt[1], ais_pt[0], ais_pt[1] )
                    if self._correlation.has_key(ais_id):
                        ''' There was already a sensor point that was matched as closest to this AIS point.
                            Let's see if current sensor point is closer (or equidistant).  If so, update the correlation'''
                        if dist <= self._correlation[ais_id][0]:
                            self._correlation[ais_id] = [dist, (sensor_pt)]
                            print 'Paired AIS ', ais_id, ' to ', self._correlation[ais_id], 'dist = ', dist, '*'
                            #self._event_api.publish( CorrelationEvent(ais_pt[0], ais_pt[1], sensor_pt[0], sensor_pt[1]))
                    else:
                        ''' No sensor point had yet been paired with this AIS point.  Update.'''
                        self._correlation[ais_id] = [dist, (sensor_pt)]
                        print 'Paired AIS ', ais_id, ' to ', self._correlation[ais_id], 'dist = ', dist
                        #self._event_api.publish( CorrelationEvent(ais_pt[0], ais_pt[1], sensor_pt[0], sensor_pt[1]))
                        
                
            for ais_id in self._correlation:
                dist, s_pt = self._correlation[ais_id]
                print 'Correlated AIS id', ais_id, 'at', self._ais_data[ais_id], 'with', s_pt, '. DIST=', dist
                self._event_api.publish( CorrelationEvent(ais_pt[0], ais_pt[1], sensor_pt[0], sensor_pt[1]), ais_uid)
            time.sleep(2)
            
    def _parse_sonar_data(self, event):
        msg = event.get_message().get_payload()
        info = msg.split()
        bearing = float(info[0])
        return bearing, info[1:]    # will always get something for the given bearing (if no ship, picks up land)
    
    def _new_sonar1_data(self, event, iface):
        msg = event.get_message().get_payload()
        print 'CA: new sonar1 data: ', msg
        info = msg.split()
        bearing = float(info[0])
        if not self._sonar1_data.has_key(bearing):
            self._sonar1_data[bearing] = []
        
        self.lock.acquire()
        for entry in info[1:]:      
            lat, lon, snr = entry.split(',')
            self._sonar1_data[bearing] = (lat, lon)
        self.lock.release()
        
    def _new_sonar2_data(self, event, iface):
        msg = event.get_message().get_payload()
        print 'CA: new sonar2 data: ', msg
        info = msg.split()
        bearing = float(info[0])
        if not self._sonar2_data.has_key(bearing):
            self._sonar2_data[bearing] = []
        
        self.lock.acquire()
        for entry in info[1:]:      # will always get something for the given bearing (if no ship, picks up land)
            lat, lon, snr = entry.split(',')
            self._sonar2_data[bearing] = (lat, lon)
        self.lock.release()
        
        
    def _new_radar1_data(self, event, iface):
        msg = event.get_message().get_payload()
        node_uid, bearing, dist, lat, lon = msg.split()
        #print 'CA: new radar1 data: ', msg
        
        if lat == "none":
            # There is no data in the current sweep
            self.lock.acquire()
            self._radar_data[bearing] = None
            self.lock.release()
            #print ' r', bearing, 
        else:
            bearing = float(bearing)    # arc sweeps may be arbitrarily small.
            lat = float(lat)
            lon = float(lon)
            
            self.lock.acquire()
            self._radar_data[bearing] = (lat, lon)
            self.lock.release()
            print 'Just added radar data at bearing ', bearing, '=', (lat, lon)
            
        
        
    def _new_ais_data(self, event, iface):
        msg = event.get_message().get_payload()
        s_id, lat, lon, agl, speed = msg.split(',')
        s_id = int(s_id)
        lat = float(lat)
        lon = float(lon)
        self._ais_data[s_id] = (lat, lon)   # ignoring agl and speed for now
        
        print 'Just added ais data at id ', s_id, '=', (lat, lon)
        
        # check if this AIS ship ID is in correlation{}.  If not, add it, default the distance to 
            
        ##this was for history
        #if s_id in self._ais_data.keys(): 
            #if len(self._ais_data[s_id]) > self._ais_hist:
            #    self._ais_data[s_id].pop(0)
            #    self._ais_data.append([lat, lon, speed])    # ignoring agl
        
    
    #def _add_sensor_pt(node_id, lat, lon):
    def _add_sensor_pt(self, lat, lon):
            
        #for pt_id, pt_lat, pt_lon in self._sensor_data:
        for pt in self._sensor_data:
            ''' See if given lat, lon point is within threshold distance of pt.
                If so, consider them the same point '''
            pass
            
            
    def _update_sensor_data(self):
        self._sensor_data = []
        
        # add radar sensor data
        ## Note: self._radar_data[bearing] = (lat, lon)
        self.lock.acquire()
        
        ''' Add RADAR sensor points to sensor_data list '''
        print 'length of radar data = ', len(self._radar_data)
        for bearing in self._radar_data:
            loc = self._radar_data[bearing]
            if loc is not None:
                self._sensor_data.append(loc)
        print 'length of sensor_data = ', len(self._sensor_data)
        
        ''' Add SONAR sensor points to sensor_data list,
            unless they are within self._ais_threshold away from one of the sensor points.
            Iterate through all sonars' sensor points combined 
            (which sonar sensor data came from does not matter at this point; 
            it only matters when trying to delete sonar data from any one particular sonar sensor only) '''
        # NOTE: Include this code once the sonar sensor sends this data over
        #all_sonar_pts = self._sonar1_data[:]
        #all_sonar_pts.extend(self._sonar2_data)
        
        #for sonar_loc in all_sonar_pts:
        #    uniquePoint = True
        #    '''make sure sonar_loc is not within ais_threshold dist from each point'''
        #    for loc in self._sensor_data:
        #        if haver_dist( sonar_loc[0], sonar_loc[1], loc[0], loc[1]) <= self._ais_threshold:
        #            uniquePoint = False
        #            break
        #    if uniquePoint:
        #        self._sensor_data.append(sonar_loc)        
        
        self.lock.release()
        

