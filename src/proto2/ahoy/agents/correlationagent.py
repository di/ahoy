from ahoy.agent import Agent
from ahoy.util.geo import *

import time, sys
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
        
        self._max_corr_dist = 0.8
        
        self._correlation = {}
        self._all_sonar_data = []
        self._ais_data = {}
        self._radar_data = {}   # keyed by bearing
        self._sonar1_data = {}  # keyed by bearing
        self._sonar2_data = {}  # keyed by bearing
        
        self._event_api = None
        
        self._sensor_history = []
        self._old_correlation = {}
        
        self._sonar_land_data = {}
        self._sonar_land_data_is_ready = False
        
        self._threats = {}
    
    
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
            self.refresh()
            time.sleep(0.5)
    
    def refresh(self):
        self.lock.acquire()
        self._correlate()
        self._detect_threats()
        self.lock.release()
        
        #time.sleep(2)
        
    
    def _correlate(self):
        
        #self.lock.acquire()
        
        '''recreate list of most recent sensor data, as it may have been updated'''
        # possibly move this action to functions where individual data points are added
        self._update_sensor_data()
        #print '*****************CORRELATING****'
        #for pt in self._all_sonar_data:
        #    print pt
        #print '\n\n'
        #for ais_id in self._ais_data:
        #    print self._ais_data[ais_id], ais_id
        #print '*************************'
        
        #self.lock.acquire()
        
        '''clear all correlations for now
            This way, there will be no chance of having an AIS ship point still correlated to an outdated
            sensor point (which may no longer even exist)'''
        # copy old correlation into new
        # used to check for duplicates. need this b/c correlation needs to start as a cleared dictionary 
        # (later we need to be able to check if all AIS ships were paired with a sensor point, before we try to find closest point to each unpaired AIS ship
        self._old_correlation.clear()
        for ais_id in self._correlation:
        	dist, s_pt = self._correlation[ais_id]
        	self._old_correlation[ais_id] = [dist, s_pt]
        self._correlation.clear()
        
        '''for each sensor data item ("current sensor item"), see which AIS data point is closest.
        If distance from the current sensor item is less than or equal to 
        the most recent smallest distance from a sensor point to this AIS data point,
        then set update the most recent smallest sensor point to be the current sensor item.'''
        
        #for sensor_pt in self._all_sonar_data:
        ''' ------------------------------------------------------------
            We now, at first, ONLY correlate with RADAR sensor points. 
            See below for sonar sensor point correlation
            ------------------------------------------------------------'''
        for sensor_pt in self._radar_data.values():
            if sensor_pt is None:
                continue
                
            #print '\nCorrelating ', sensor_pt, '...'
            ''' distance to AIS ship should be negligent '''
            closest_dist = self._max_corr_dist  #self._ais_threshold #self._ais_threshold  #99999
            closest_ais_id = None
            
            for ais_id in self._ais_data:
                ais_pt = self._ais_data[ais_id]
                try:
                    dist = haver_distance( sensor_pt[0], sensor_pt[1], ais_pt[0], ais_pt[1] )
                except:
                    print 'sensor pt = ', sensor_pt
                    print 'ais_pt = ', ais_pt
                #print 'dist = ', dist
                
                if dist < closest_dist:
                    # Only match if we find an AIS point closer than we have found before
                    closest_dist = dist
                    closest_ais_id = ais_id
                    #print 'closest_ais_id = ', closest_ais_id, 'closest_dist = ', closest_dist
                    #print 'Found a new closest distance: ', closest_dist
            
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
                    #print 'OVERWRITE: Paired this sensor pt to AIS ', closest_ais_id, 'dist=', closest_dist, '*'
            else:
                ''' No sensor point had yet been paired with this AIS point,
                    and we know this is the closest AIS point we've found to this sensor so far.  Update.'''
                self._correlation[closest_ais_id] = [closest_dist, (sensor_pt)]
                #print 'Paired this sensor pt to AIS ', closest_ais_id, 'dist=', closest_dist
        
        
        for ais_id in self._correlation:
            ais_pt = self._ais_data[ais_id]
            dist, s_pt = self._correlation[ais_id]
            #print 'Correlated AIS id', ais_id, 'at', self._ais_data[ais_id], 'with', s_pt, '. DIST=', dist
            #self._event_api.publish( CorrelationEvent(ais_pt[0], ais_pt[1], s_pt[0], s_pt[1], ais_id))
            self._publish_correlation(ais_id, ais_pt, dist, s_pt)
            
        ''' update all blank AIS matches'''
        # first, create list of unmatched sensor points
        available_sensor_pts = []
        #for pt in self._all_sonar_data:
        for pt in self._radar_data.values():
            if pt is None:
                continue
            if pt not in self._correlation.values():
                available_sensor_pts.append(pt)
                
        for ais_id in self._ais_data:
            if not ais_id in self._correlation:
                #print 'About to correlate AIS ID', ais_id, ', which so far was unmatched.'
                ais_pt = self._ais_data[ais_id]
                
                closest_dist, closest_pt = self._get_closest_pt(ais_pt, available_sensor_pts)
                if closest_pt is None:
                    print 'No radar point correlated with AIS ID', ais_id
                    #self._event_api.publish( CorrelationEvent(ais_pt[0], ais_pt[1], ais_pt[0], ais_pt[1], ais_id))
                    self._correlation[ais_id] = [0, ais_pt]
                    self._publish_correlation(ais_id, ais_pt, 0, ais_pt)
                else:
                    
                    if closest_dist <= self._max_corr_dist:
                        print 'Correlating with closest radar pt ', closest_pt, ' dist = ', closest_dist
                        self._correlation[ais_id] = [closest_dist, closest_pt]
                        available_sensor_pts.remove(closest_pt)
                        #self._event_api.publish( CorrelationEvent(ais_pt[0], ais_pt[1], closest_pt[0], closest_pt[1], ais_id))
                        self._publish_correlation(ais_id, ais_pt, closest_dist, closest_pt)
                    else:
                        print 'No radar point correlated with AIS ID', ais_id, '. closest_d = ', closest_dist
                        #print 'No sensor point correlated with AIS ID', ais_id, 'at', ais_pt, '. closest_d = ', closest_dist
                        #self._event_api.publish( CorrelationEvent(ais_pt[0], ais_pt[1], ais_pt[0], ais_pt[1], ais_id))
                        self._correlation[ais_id] = [0, ais_pt]
                        self._publish_correlation(ais_id, ais_pt, 0, ais_pt)
        
        ''' ------------------------------------------------------
            Now, correlate any of the sonar sensor data points
            ------------------------------------------------------'''
        available_sonar_pts = self._all_sonar_data[:]
        
        for ais_id in self._ais_data:
            # Need new key so as not to duplicate key in self._correlation for radar point correlations
            sonar_ais_key = str(ais_id) + 's'
            ais_pt = self._ais_data[ais_id]
            
            closest_dist, closest_pt = self._get_closest_pt(ais_pt, available_sonar_pts)
            
            if closest_pt is None:
                ''' No closest point. Update to publish as correlation with self.'''
                self._correlation[sonar_ais_key] = [0, ais_pt]
                self._publish_correlation(ais_id, ais_pt, 0, ais_pt, sonar_ais_key)
                #print 'No SONAR point correlated with AIS ID', ais_id
            else:
                ''' Found a closest point, not necessarily within self._max_corr_dist'''
                if closest_dist <= self._max_corr_dist:
                    self._correlation[sonar_ais_key] = [closest_dist, closest_pt]
                    available_sonar_pts.remove(closest_pt)
                    self._publish_correlation(ais_id, ais_pt, closest_dist, closest_pt, sonar_ais_key)
                    #print 'Correlating with closest SONAR pt ', closest_pt, ' dist = ', closest_dist
                    
                else:
                    ''' Closest point is too far away.  Publish as correlation with self.'''
                    self._correlation[sonar_ais_key] = [0, ais_pt]
                    self._publish_correlation(ais_id, ais_pt, 0, ais_pt, sonar_ais_key)
                    #print 'No SONAR point correlated with AIS ID', ais_id, '. closest_d = ', closest_dist
        
        self._old_correlation.clear()
        #self.lock.release()
    
    
    def _publish_correlation(self, ais_id, ais_pt, dist, s_pt, ais_key=None):
        if ais_key is None:
            ais_key = ais_id
        
        publish_event = False
        if ais_key in self._old_correlation:
            old_dist, old_pt = self._old_correlation[ais_key]
            if not old_pt == s_pt:
                publish_event = True
        else:
            publish_event = True
            
        if publish_event:
            self._event_api.publish( CorrelationEvent(ais_pt[0], ais_pt[1], s_pt[0], s_pt[1], ais_id))
            print 'Correlated AIS id', ais_key, 'at', ais_pt, 'with', s_pt, '. DIST=', dist
            
    
    def _get_closest_pt(self, loc, pts):
        closest_dist = 99999
        closest_pt = None
        
        for pt in pts:
            dist = haver_distance(pt[0], pt[1], loc[0], loc[1])
            if dist < closest_dist:
                closest_dist = dist
                closest_pt = pt
        return [closest_dist, closest_pt]
    
    
    def _publish_threat(self, ais_id, sensor_pt, d):
        if not ais_id in self._threats:
            self._threats[ais_id] = []
        
        if not sensor_pt in self._threats[ais_id]:
            print 'DETECTED THREAT at ', sensor_pt, ' to AIS ID', ais_id, ' d=', d
            self._event_api.publish( ProximityThreatEvent(sensor_pt[0], sensor_pt[1], ais_id))
            self._threats[ais_id].append(sensor_pt)
        #else:
        #    print sensor_pt, ' is already in ', self._threats[ais_id]
    
    
    def _detect_threats(self):
        #self.lock.acquire()
        
        ''' Get list of all sensor points that were correlated '''
        correlated_s_pts = []
        for dist, s_pt in self._correlation.values():
            correlated_s_pts.append( s_pt )
        
        ''' Create cumulative list of all sensor data '''
        all_sensor_data = self._all_sonar_data[:]
        all_sensor_data.extend( self._radar_data.values() )
        
        ''' Go through all sensor points that were reported to agent...'''    
        for sensor_pt in all_sensor_data:
            if sensor_pt is None:
                continue
            if not sensor_pt in correlated_s_pts:
                
                ''' This sensor_pt was not correlated with an AIS ship.  It is a possible threat.
                    Check if the sensor_pt is within self._threat_dist of an AIS ship'''
                for ais_id in self._ais_data:
                    ais_pt = self._ais_data[ais_id]
                    d = haver_distance( sensor_pt[0], sensor_pt[1], ais_pt[0], ais_pt[1] )
                    if d <= self._threat_dist:
                        self._publish_threat(ais_id, sensor_pt, d)
                        
                        #if not ais_id in self._correlation:
                        #    print '\tthis AIS ID was not correlated.'
                        #else:
                        #    print '\tAIS ID', ais_id, 'was correlated: ', self._correlation[ais_id]
        #self.lock.release()
        
        
    
    
    def _pt_in_sonar_land_data(self, pt):
        if pt in self._sonar_land_data:
            if self._sonar_land_data[pt] > 4:
                return True
        return False
    
    def _check_sonar_land_data(self, pt):
        #if self._pt_in_sonar_land_data(pt):
        if pt in self._sonar_land_data:
            
            # Test if land data is ready
            if (not self._sonar_land_data_is_ready) and (self._sonar_land_data[pt] > 5):
                self._sonar_land_data_is_ready = True
                print 'SONAR LAND DATA IS READY.'
            
            #self._sonar_land_data[pt] = self._sonar_land_data[pt] + 1
            self._sonar_land_data[pt] += 1
            #print 'land pt repeat count = ', self._sonar_land_data[pt]
            return True
        
        else:
            #print 'new possible land pt:', pt
            self._sonar_land_data[pt] = 1   # start count at 1
        
        return False
    
    
    
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
        
        self.lock.acquire()
        if not self._sonar1_data.has_key(bearing):
            self._sonar1_data[bearing] = None
        
        for entry in info[1:]:      
            lat, lon, snr = entry.split(',')
            lat = float(lat)
            lon = float(lon)
            #if (not self._sonar1_data.has_key(bearing)) or (not (lat,lon) is self._sonar1_data[bearing]):
            #    print 'updated sonar1 data bearing', bearing, ' = ', (lat, lon)
            self._sonar1_data[bearing] = (lat, lon)
        self.lock.release()
        
        #is_land_pt = self._check_sonar_land_data( (lat,lon) )
        #if not is_land_pt:
        #    self.refresh()
        #else:
        #    print (lat,lon), 'is a land point'
        
        
    def _new_sonar2_data(self, event, iface):
        msg = event.get_message().get_payload()
        #print 'CA: new sonar2 data: ', msg
        info = msg.split()
        bearing = float(info[0])
        
        self.lock.acquire()
        if not self._sonar2_data.has_key(bearing):
            self._sonar2_data[bearing] = None
        
        for entry in info[1:]:      # will always get something for the given bearing (if no ship, picks up land)
            lat, lon, snr = entry.split(',')
            lat = float(lat)
            lon = float(lon)
            #if (not self._sonar2_data.has_key(bearing)) or (not (lat,lon) is self._sonar2_data[bearing]):
            #    print 'updated sonar2 data bearing', bearing, ' = ', (lat, lon)
            self._sonar2_data[bearing] = (lat, lon)
        self.lock.release()
        
        self._check_sonar_land_data( (lat,lon) )
        
        #is_land_pt = self._check_sonar_land_data( (lat,lon) )
        #if not is_land_pt:
        #    self.refresh()
        #else:
        #    print (lat,lon), 'is a land point'
        
        
    def _new_radar1_data(self, event, iface):
        msg = event.get_message().get_payload()
        node_uid, bearing, dist, lat, lon = msg.split()
        #print 'CA: new radar1 data: ', msg
        
        if lat == "none":
            # There is no data in the current sweep
            self.lock.acquire()
            self._radar_data[bearing] = None
            self.lock.release()
        else:
            bearing = float(bearing)    # arc sweeps may be arbitrarily small.
            lat = float(lat)
            lon = float(lon)
            
            self.lock.acquire()
            #if (not self._radar_data.has_key(bearing)) or (not (lat,lon) is self._radar_data[bearing]):
            #        print 'Just added radar data at bearing ', bearing, '=', (lat, lon)
            self._radar_data[bearing] = (lat, lon)
            self.lock.release()
        
        #self.refresh()
        
        
    def _new_ais_data(self, event, iface):
        msg = event.get_message().get_payload()
        print 'new ais msg: ', msg
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
        
        #self.refresh()
        
        
    def _update_sensor_data(self):
        ''' This method adds all SONAR sensor points to self._all_sonar_data.
            Sonar sensor points are no
                closest_dist, closest_pt = self._get_closest_pt(ais_pt, available_sensor_pts)t added if they appear to be land points.
            '''
        self._all_sonar_data = []
        
        # add radar sensor data
        ## Note: self._radar_data[bearing] = (lat, lon)
        
        ''' Add RADAR sensor points to sensor_data list '''
        ''' We no longer include these, because we need self._all_sonar_data to ONLY include non-radar sensor points (i.e. sonar pts).
            This is so we can correlate each set separately (instead of removing what appear to be duplicate sensor pts)
            '''
        #print 'length of radar data = ', len(self._radar_data)
        #for bearing in self._radar_data:
        #    loc = self._radar_data[bearing]
        #    if loc is not None:
        #        self._all_sonar_data.append(loc)
        #print 'length of sensor_data (radar) = ', len(self._all_sonar_data)
        
        ''' Add SONAR sensor points to sensor_data list,
            unless they are within self._ais_threshold away from one of the sensor points.
            Iterate through all sonars' sensor points combined 
            (which sonar sensor data came from does not matter at this point; 
            it only matters when trying to delete sonar data from any one particular sonar sensor only) '''
        
        if not self._sonar_land_data_is_ready:
            #print 'sonar data is not ready yet.'
            return
        
        all_sonar_pts = []
        all_sonar_pts.extend( self._sonar1_data.values() )
        all_sonar_pts.extend( self._sonar2_data.values() )
        #print 'length of all_sonar_pts = ', len(all_sonar_pts)
        
        for sonar_loc in all_sonar_pts:
            if sonar_loc is None:
                continue
                
            if self._pt_in_sonar_land_data(sonar_loc) is True:
                ''' This is a land point'''
                #print sonar_loc, 'is a land pt'
                continue
            
            self._all_sonar_data.append(sonar_loc)
            
            
            ''' We no longer do this, because we will correlate BOTH a radar and a sonar point to each AIS ship (if it is within range).
                Add this code back in to remove what appear to be duplicate sensor points.
                These would be any sonar points that are within self._ais_threshold of a radar point, and would be deleted.'''
            #uniquePoint = True
            #'''make sure sonar_loc is not within ais_threshold dist from any radar point'''
            #for loc in self._radar_data.values():
            #    if loc is None:
            #        continue
            #    #print 'about to calculate haver_distance for ', sonar_loc, 'and', loc
            #    try:
            #        if haver_distance( sonar_loc[0], sonar_loc[1], loc[0], loc[1]) <= self._ais_threshold:
            #            uniquePoint = False
            #            break
            #    except:
            #        print 'error with sonar_loc = ', sonar_loc, ', loc = ', loc
            #if uniquePoint:
            #    self._all_sonar_data.append(sonar_loc)
        #print 'length of self._all_sonar_data = ', len(self._all_sonar_data) 
        
        

