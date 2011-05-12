from ahoy.agent import Agent
from ahoy.util.geo import *

import time
from threading import Lock

from ahoy.eventapi import EventAPI
from ahoy.events.correlation import CorrelationEvent
from ahoy.events.prox_threat import ProximityThreatEvent

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
        self._ais_threshold = ais_threshold
        
        self._max_corr_dist = 1.0
        
        self._correlation = {}
        self._sensor_data = []
        self._ais_data = {}
        self._radar_data = {}   # keyed by bearing
        self._sonar1_data = {}  # keyed by bearing
        self._sonar2_data = {}  # keyed by bearing
        
        self._event_api = None
        
        self._sensor_history = []
    
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
            self.lock.acquire()
            
            '''recreate list of most recent sensor data, as it may have been updated'''
            # possibly move this action to functions where individual data points are added
            self._update_sensor_data()
            print '*****************CORRELATING****'
            for pt in self._sensor_data:
                print pt
            print '\n\n'
            for ais_id in self._ais_data:
                print self._ais_data[ais_id], ais_id
            print '*************************'
            
            #self.lock.acquire()
            
            '''clear all correlations for now
                This way, there will be no chance of having an AIS ship point still correlated to an outdated
                sensor point (which may no longer even exist)'''
            self._correlation.clear()
            
            '''for each sensor data item ("current sensor item"), see which AIS data point is closest.
            If distance from the current sensor item is less than or equal to 
            the most recent smallest distance from a sensor point to this AIS data point,
            then set update the most recent smallest sensor point to be the current sensor item.'''
            
            #for ais_id in self._ais_data[ais_id]:
            #    ais_pt = self._ais_data[ais_id]
            for sensor_pt in self._sensor_data:
            #for sensor_pt in self._radar_data.values():
            
                print '\nCorrelating ', sensor_pt, '...'
                ''' distance to AIS ship should be negligent '''
                closest_dist = self._max_corr_dist  #self._ais_threshold #self._ais_threshold  #99999
                closest_ais_id = None
                #closest_s_pt = None
                
                #for sensor_pt in self._sensor_data:
                for ais_id in self._ais_data:
                    ais_pt = self._ais_data[ais_id]
                    dist = haver_distance( sensor_pt[0], sensor_pt[1], ais_pt[0], ais_pt[1] )
                    #print 'dist = ', dist
                    
                    if dist < closest_dist:
                        # Only match if we find an AIS point closer than we have found before
                        closest_dist = dist
                        closest_ais_id = ais_id
                        #closest_s_pt = None
                        #print 'closest_ais_id = ', closest_ais_id, 'closest_dist = ', closest_dist
                        print 'Found a new closest distance: ', closest_dist
                
                #print 'closest_ais_id = ', closest_ais_id
                if closest_ais_id is None:
                #if closest_s_pt = None:
                    continue
                
                ''' Now that we know which AIS data point is closest to this sensor_pt...'''
                if self._correlation.has_key(closest_ais_id):
                    ''' There was already a sensor point that was matched as closest to this AIS point.
                        Let's see if current sensor point is closer (or equidistant).  If so, update the correlation'''
                    if closest_dist <= self._correlation[closest_ais_id][0]:
                        self._correlation[closest_ais_id] = [closest_dist, (sensor_pt)]
                        print 'OVERWRITE: Paired this sensor pt to AIS ', closest_ais_id, 'dist=', closest_dist, '*'
                else:
                    ''' No sensor point had yet been paired with this AIS point,
                        and we know this is the closest AIS point we've found to this sensor so far.  Update.'''
                    self._correlation[closest_ais_id] = [closest_dist, (sensor_pt)]
                    print 'Paired this sensor pt to AIS ', closest_ais_id, 'dist=', closest_dist
                    
                    
            #print 'final:'
            for ais_id in self._correlation:
                ais_pt = self._ais_data[ais_id]
                dist, s_pt = self._correlation[ais_id]
                print 'Correlated AIS id', ais_id, 'at', self._ais_data[ais_id], 'with', s_pt, '. DIST=', dist
                self._event_api.publish( CorrelationEvent(ais_pt[0], ais_pt[1], s_pt[0], s_pt[1], ais_id))
                
            ''' update all blank AIS matches'''
            # first, create list of unmatched sensor points
            available_sensor_pts = []
            for pt in self._sensor_data:
                if pt not in self._correlation.values():
                    available_sensor_pts.append(pt)
                    
            for ais_id in self._ais_data:
                if not ais_id in self._correlation:
                    print 'About to correlate AIS ID', ais_id, ', which so far was unmatched.'
                    ais_pt = self._ais_data[ais_id]
                    
                    closest_dist, closest_pt = self._get_closest_pt(ais_pt, available_sensor_pts)
                    if closest_pt is None:
                        print 'No sensor point correlated with AIS ID', ais_id, 'at', ais_pt, '!'
                        self._event_api.publish( CorrelationEvent(ais_pt[0], ais_pt[1], ais_pt[0], ais_pt[1], ais_id))
                    else:
                        print 'Found closest point ', closest_pt, ' dist = ', closest_dist
                        if closest_dist <= self._max_corr_dist:
                            self._correlation[ais_id] = [closest_dist, closest_pt]
                            self._event_api.publish( CorrelationEvent(ais_pt[0], ais_pt[1], closest_pt[0], closest_pt[1], ais_id))
                    
                    #print 'No sensor point correlated with AIS ID ', ais_id, ' at ', ais_pt
                    #self._event_api.publish( CorrelationEvent(ais_pt[0], ais_pt[1], ais_pt[0], ais_pt[1], ais_id))
                    
            #self.lock.release()
            
            self._detect_threats()
            self.lock.release()
            
            time.sleep(2)
    
    def _get_closest_pt(self, loc, pts):
        closest_dist = 99999
        closest_pt = None
        
        for pt in pts:
            dist = haver_distance(pt[0], pt[1], loc[0], loc[1])
            if dist < closest_dist:
                closest_dist = dist
                closest_pt = pt
        return [closest_dist, closest_pt]
    
    
    def _detect_threats(self):
        #self.lock.acquire()
        
        ''' Get list of all sensor points that were correlated '''
        correlated_s_pts = []
        for dist, s_pt in self._correlation.values():
            correlated_s_pts.append( s_pt )
        
        ''' Go through all sensor points that were reported to agent...'''    
        for sensor_pt in self._sensor_data:
            if not sensor_pt in correlated_s_pts:
                
                ''' This sensor_pt was not correlated with an AIS ship.  It is a possible threat.
                    Check if the sensor_pt is within self._threat_dist of an AIS ship'''
                for ais_id in self._ais_data:
                    ais_pt = self._ais_data[ais_id]
                    if haver_distance( sensor_pt[0], sensor_pt[1], ais_pt[0], ais_pt[1] ) <= self._threat_dist:
                        print 'POSSIBLE THREAT at ', sensor_pt
                        self._event_api.publish( ProximityThreatEvent(sensor_pt[0], sensor_pt[1], ais_id))
        #self.lock.release()
            
        
    
    def _parse_sonar_data(self, event):
        msg = event.get_message().get_payload()
        info = msg.split()
        bearing = float(info[0])
        return bearing, info[1:]    # will always get something for the given bearing (if no ship, picks up land)
    
    def _new_sonar1_data(self, event, iface):
        msg = event.get_message().get_payload()
        #print 'CA: new sonar1 data: ', msg
        info = msg.split()
        bearing = float(info[0])
        if not self._sonar1_data.has_key(bearing):
            self._sonar1_data[bearing] = []
        
        self.lock.acquire()
        for entry in info[1:]:      
            lat, lon, snr = entry.split(',')
            lat = float(lat)
            lon = float(lon)
            self._sonar1_data[bearing] = (lat, lon)
        self.lock.release()
        
    def _new_sonar2_data(self, event, iface):
        msg = event.get_message().get_payload()
        #print 'CA: new sonar2 data: ', msg
        info = msg.split()
        bearing = float(info[0])
        if not self._sonar2_data.has_key(bearing):
            self._sonar2_data[bearing] = []
        
        self.lock.acquire()
        for entry in info[1:]:      # will always get something for the given bearing (if no ship, picks up land)
            lat, lon, snr = entry.split(',')
            lat = float(lat)
            lon = float(lon)
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
            #print 'Just added radar data at bearing ', bearing, '=', (lat, lon)
            
        
        
    def _new_ais_data(self, event, iface):
        msg = event.get_message().get_payload()
        s_id, lat, lon, agl, speed = msg.split(',')
        s_id = int(s_id)
        lat = float(lat)
        lon = float(lon)
        self.lock.acquire()
        #if self._ais_data.has_key(s_id):
        #    dist = haver_distance(lat, lon, self._ais_data[s_id][0], self._ais_data[s_id][1])
        #    print 'dist between last AIS data = ', dist
        self._ais_data[s_id] = (lat, lon)   # ignoring agl and speed for now
        self.lock.release()
        
        #print 'Just added ais data at id ', s_id, '=', (lat, lon)
        
    
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
        #self.lock.acquire()
        
        ''' Add RADAR sensor points to sensor_data list '''
        #print 'length of radar data = ', len(self._radar_data)
        for bearing in self._radar_data:
            loc = self._radar_data[bearing]
            if loc is not None:
                self._sensor_data.append(loc)
        #print 'length of sensor_data = ', len(self._sensor_data)
        
        ''' Add SONAR sensor points to sensor_data list,
            unless they are within self._ais_threshold away from one of the sensor points.
            Iterate through all sonars' sensor points combined 
            (which sonar sensor data came from does not matter at this point; 
            it only matters when trying to delete sonar data from any one particular sonar sensor only) '''
        
        all_sonar_pts = []
        all_sonar_pts.extend( self._sonar1_data.values() )
        all_sonar_pts.extend( self._sonar2_data.values() )
        #print 'length of all_sonar_pts = ', len(all_sonar_pts)
        
        for sonar_loc in all_sonar_pts:
            uniquePoint = True
            '''make sure sonar_loc is not within ais_threshold dist from each point'''
            for loc in self._sensor_data:
                #print 'about to calculate haver_distance for ', sonar_loc, 'and', loc
                if haver_distance( sonar_loc[0], sonar_loc[1], loc[0], loc[1]) <= self._ais_threshold:
                    uniquePoint = False
                    break
            if uniquePoint:
                self._sensor_data.append(sonar_loc)
        #print 'length of self._sensor_data = ', len(self._sensor_data) 
        
        #self.lock.release()
        

