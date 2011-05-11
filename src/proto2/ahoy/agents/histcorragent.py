from ahoy.agent import Agent
from ahoy.util.geo import *

import time
from threading import Lock

from ahoy.eventapi import EventAPI
from ahoy.events.correlation import CorrelationEvent
from ahoy.events.prox_threat import ProximityThreatEvent

class HistoryCorrelationAgent(Agent):
    
    def __init__(self, uid, threat_dist, ais_threshold, iface_s1, iface_s2, iface_r1, iface_ais, history_num, s_accuracy, threat_step) :
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
        
        # Number of sensor data points to keep in history per correlated set
        self._history_num = history_num
        # Max distance the sensor data can be apart to be considered the same sensor point
        self._sensor_accuracy = s_accuracy
        # How quickly to change threat level from new data (weight of old threat level vs new). (0,1]
        self._threat_step = threat_step
        
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
            
            '''recreate list of most recent sensor data, as it may have been updated'''
            # possibly move this action to functions where individual data points are added
            self._update_sensor_data()
            #print '*****************CORRELATING****'
            #for pt in self._sensor_data:
            #    print pt
            #print '\n\n'
            #for ais_id in self._ais_data:
            #    print self._ais_data[ais_id], ais_id
            #print '*************************'
            
            self.lock.acquire()
            
            '''clear all correlations for now
                This way, there will be no chance of having an AIS ship point still correlated to an outdated
                sensor point (which may no longer even exist)'''
            self._correlation.clear()
            
            '''for each sensor data item ("current sensor item"), see which AIS data point is closest.
            If distance from the current sensor item is less than or equal to 
            the most recent smallest distance from a sensor point to this AIS data point,
            then set update the most recent smallest sensor point to be the current sensor item.'''
            
            for sensor_pt in self._sensor_data:
                #print '\nCorrelating ', sensor_pt, '...'
                closest_dist = 99999
                closest_ais_id = None
                
                for ais_id in self._ais_data:
                    ais_pt = self._ais_data[ais_id]
                    dist = haver_distance( sensor_pt[0], sensor_pt[1], ais_pt[0], ais_pt[1] )
                    
                    if dist < closest_dist:
                        # Only match if we find an AIS point closer than we have found before
                        closest_dist = dist
                        closest_ais_id = ais_id
                
                if closest_ais_id is None:
                    continue
                
                ''' Now that we know which AIS data point is closest to this sensor_pt...'''
                if self._correlation.has_key(closest_ais_id):
                    ''' There was already a sensor point that was matched as closest to this AIS point.
                        Let's see if current sensor point is closer (or equidistant).  If so, update the correlation'''
                    if closest_dist <= self._correlation[closest_ais_id][0]:
                        self._correlation[closest_ais_id] = [closest_dist, (sensor_pt)]
                        #print 'Paired this sensor pt to AIS ', closest_ais_id, 'dist=', closest_dist, '*'
                else:
                    ''' No sensor point had yet been paired with this AIS point,
                        and we know this is the closest AIS point we've found to this sensor so far.  Update.'''
                    self._correlation[closest_ais_id] = [closest_dist, (sensor_pt)]
                    #print 'Paired this sensor pt to AIS ', closest_ais_id, 'dist=', closest_dist
                    
                    
            #print 'final:'
            for ais_id in self._correlation:
                ais_pt = self._ais_data[ais_id]
                dist, s_pt = self._correlation[ais_id]
                #print 'Correlated AIS id', ais_id, 'at', self._ais_data[ais_id], 'with', s_pt, '. DIST=', dist
                self._event_api.publish( CorrelationEvent(ais_pt[0], ais_pt[1], s_pt[0], s_pt[1], ais_id))
                
            # update all blank AIS matches
            for ais_id in self._ais_data:
                if not ais_id in self._correlation:
                    ais_pt = self._ais_data[ais_id]
                    self._event_api.publish( CorrelationEvent(ais_pt[0], ais_pt[1], ais_pt[0], ais_pt[1], ais_id))
                    
            self.lock.release()
            
            ''' move sensor data to history, 
                while correlating the most recent sensor data w/ historical sensor data'''
            self._correlate_sensor_history()
            #self._detect_threats()
            
            time.sleep(3)
            
    
    
    def _get_sensor_hist_by_pt(self, pt):
        #self.lock.acquire()
        pt = None
        for info in self._sensor_history:
            if info[1] == pt:
                pt = info
                break
        #self.lock.release()
        return pt
        
    
    def _correlate_sensor_history(self):
        print '\nCorrelating sensor history...'
        self.lock.acquire() 
        
        ''' If there is no most recent sensor data, ignore this '''
        if len(self._sensor_data) == 0:
            print 'No sensor data. Exiting function.'
            self.lock.release()
            return
        
        hist_correlation = {}
        print 'len of sensor data = ', len(self._sensor_data)
        print 'len of history data = ', len(self._sensor_history)
        
        for new_pt in self._sensor_data:
            ''' Try to correlate each new sensor pt to historical points.
                If none are less than self._sensor_accuracy km away,
                consider this a new sensor point'''
            print '\nCorrelating', new_pt
            
            closest_dist = self._sensor_accuracy
            closest_pt = None
            
            for hist in self._sensor_history:
                hist_pt = hist[1]
                
                dist = haver_distance( hist_pt[0], hist_pt[1], new_pt[0], new_pt[1] )
                
                if dist < closest_dist:
                    closest_dist = dist
                    closest_pt = hist_pt
                #else:
                #    print 'point too far away, dist = ', dist
                    
            if closest_pt is None:
                print 'Could not find closest sensor pt history match for ', new_pt, '. Adding it as new entry.'
                self._sensor_history.append([0, new_pt])
                continue
            
            ''' Update hist_correlation'''
            if hist_correlation.has_key( closest_pt ):
                if closest_dist <= hist_correlation[closest_pt][0]:
                    print 'bumping out ', hist_correlation[closest_pt], 'with new data: ', new_pt, ', d = ', closest_dist
                    hist_correlation[closest_pt] = [closest_dist, new_pt]
                    
            else:
                print 'assigning ', closest_pt, ' as correlation. d = ', closest_dist
                hist_correlation[closest_pt] = [closest_dist, new_pt]
        
        ''' Update self._sensor_history with new correlations'''
        ''' This is the part where we tack on new set of sensor points, to their corresponding (correlated)
            historical sensor points.
            We iterate through all these already existing historical sensor data points, to which new ones were correlated to,
            and tack on the new points into the old ones' historical list.
            If a new sensor point was not correlated with a historical point, it was added above.'''
        for correlated_hist_pt in hist_correlation:
            dist, new_hist_pt = hist_correlation[correlated_hist_pt]
            inserted_new_pt = False
            
            for hist_info in self._sensor_history:
                if correlated_hist_pt == hist_info[1]:
                    ''' This is the item (list, technically) in self._sensor_history 
                        where we need to tack on the newly correlated sensor pt'''
                    hist_info.insert(1, new_hist_pt)
                    print 'Just inserted ', new_hist_pt, ' into ', hist_info
                    if len(hist_info) > self._history_num :
                        hist_info.pop(-1)   # the last item is the value of the threat, NOT a historical point
                    inserted_new_pt = True
                    break
            
            if not inserted_new_pt:
                print 'Did not insert', new_hist_pt, ' into correlation history. Problem.'
        
        self.lock.release()
        
        print '\t..finished correlating sensor history.'
            
                
                
        
        
    
    def _detect_threats(self):
        print 'Detecting threats...'
        self.lock.acquire()
        
        print len(self._correlation), ' = length of self._correlation'
        ''' Get list of all sensor points that were correlated '''
        correlated_s_pts = []
        for dist, s_pt in self._correlation.values():
            correlated_s_pts.append( s_pt )
        print len(correlated_s_pts), 'correlated sensor points.'
        print len(self._correlation), 'keys in self._correlation'
        
        ''' Go through all sensor points that were reported to agent...'''    
        for sensor_pt in self._sensor_data:
            #print 'analyzing ', sensor_pt
            hist_info = self._get_sensor_hist_by_pt(sensor_pt)
            print hist_info

            if not sensor_pt in correlated_s_pts:
                #if hist_info is not None:
                #    ''' adjust hist_info. check if threat level is high for this sensor point'''
                
                ''' This sensor_pt was not correlated with an AIS ship.  It is a possible threat.
                    Check if the sensor_pt is within self._threat_dist of an AIS ship'''
                for ais_id in self._ais_data:
                    ais_pt = self._ais_data[ais_id]
                    
                    dist = haver_distance( sensor_pt[0], sensor_pt[1], ais_pt[0], ais_pt[1] )
                    
                    if dist <= self._threat_dist:
                        if hist_info is not None:
                            threat_level = hist_info[0]
                            new_threat_level = (self._threat_dist - dist) / self._threat_dist
                            threat_level = self._threat_step*threat_level + (1-self._threat_level)*new_threat_level
                            hist_info[0] = threat_level
                            
                            if threat_level > 0.5:
                                print 'POSSIBLE THREAT at ', sensor_pt
                                self._event_api.publish( ProximityThreatEvent(sensor_pt[0], sensor_pt[1], ais_id))
                            else:
                                print sensor_pt, 'is not quite a threat yet..'
                        else:
                            'No sensor data history for ', sensor_pt
                            if dist <= (0.5*self._threat_dist):
                                print 'POSSIBLE THREAT at ', sensor_pt, '. reporting WITHOUT historical data.'
                                self._event_api.publish( ProximityThreatEvent(sensor_pt[0], sensor_pt[1], ais_id))
            else:
                print '\t\tthis point was correlated.'
                if hist_info is not None:
                    # If point was correlated to AIS data, set its threat level to 0 (it may already be at that amount)
                    hist_info[0] = 0
                    
                
        self.lock.release()
        print 'Done detecting threats.'
            
        
    
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
        self._ais_data[s_id] = (lat, lon)   # ignoring agl and speed for now
        self.lock.release()
        
        #print 'Just added ais data at id ', s_id, '=', (lat, lon)
        
        # check if this AIS ship ID is in correlation{}.  If not, add it, default the distance to 
            
        ##this was for history
        #if s_id in self._ais_data.keys(): 
            #if len(self._ais_data[s_id]) > self._ais_hist:
            #    self._ais_data[s_id].pop(0)
            #    self._ais_data.append([lat, lon, speed])    # ignoring agl
        
    
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
        
        #all_sonar_pts = []
        #all_sonar_pts.extend( self._sonar1_data.values() )
        #all_sonar_pts.extend( self._sonar2_data.values() )
        #print 'length of all_sonar_pts = ', len(all_sonar_pts)
        
        #for sonar_loc in all_sonar_pts:
        #    uniquePoint = True
        #    '''make sure sonar_loc is not within ais_threshold dist from each point'''
        #    for loc in self._sensor_data:
        #        if haver_distance( sonar_loc[0], sonar_loc[1], loc[0], loc[1]) <= self._ais_threshold:
        #            uniquePoint = False
        #            break
        #    if uniquePoint:
        #        self._sensor_data.append(sonar_loc)
        print 'length of self._sensor_data = ', len(self._sensor_data) 
        
        self.lock.release()
        

