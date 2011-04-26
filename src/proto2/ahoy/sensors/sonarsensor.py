import random
import math
import time
from ahoy.sensor import Sensor
from ahoy.events.sensor import SensorEvent
from ahoy.util.geo import *
from ahoy.util.height import Elevation

class SonarEvent(SensorEvent) :
    def __init__(self, owner_uid, bearing, detects) :
        SensorEvent.__init__(self, owner_uid)
        self._bearing = bearing
        self._detects = detects

    def get_bearing(self) :
        return self._bearing

    def get_detects(self) :
        return self._detects

    def __str__(self) :
        '''
                s = ''
                for bearing, detect in self._detects.iteritems() :
                    print bearing, detect
                    s += '%s %s %s\n' % (bearing, detect[0][0], detect[0][1]) # TODO: Fix for multiple pings per bearing
                print 'msg len:', len(s)
        '''
        s = ''
        for det in self._detects :
            dist, snr = det
            s += '%s,%s ' % (dist, snr)
        print self._bearing, self._detects, '%s %s' % (self._bearing, s.strip())
        return '%s %s' % (self._bearing, s.strip())

class SonarSensor(Sensor) :
    def __init__(self, source_level, source_bw, array_size, interval, min_snr, angular=False, noise_mean=50, noise_std=5) :
        Sensor.__init__(self)
        self._source_level = source_level # dB
        self._source_bw = source_bw
        self._angles = 360 / array_size
        self._interval = interval
        self._min_snr = min_snr
        self._angular = angular
        
        self._noise_mean = noise_mean
        self._noise_std = noise_std
        self._elevation = Elevation()

    def _get_edges(self) :
        edges = []
        lat, lon, agl = self.get_owner().get_position()
        for angle in range(0, 360) :
            e_lat, e_lon, e_dist, e_height = self._elevation.get_above(lat, lon, angle)
            edges.append([e_dist, self._get_snr(e_dist * 1000, 0)])
        return edges

    def _get_noise(self) :
       return random.gauss(self._noise_mean, self._noise_std)

    def _get_sound_speed(self, depth) :
        # Based on http://en.wikipedia.org/wiki/Speed_of_sound#Seawater.
        # T, S, and z will vary by region and shouldn't be hardcoded
        t = 25
        s = 35
        d = abs(depth)
        return 1448.96+4.591*t-(5.304e-2)*t**2+(2.374e-4)*t**3+1.340*(s-35)+(1.630e-2)*d+(1.675e-7)*d**2-(1.025e-2)*t*(s-35)-(7.139e-13)*t*d**3

    def _get_prop_time(self, src, target) :
        x, y = a
        distance = math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)
        n = distance
        theta = math.atan2(b[1] - a[1], b[0] - a[0])
        total = (distance / n) / self._get_sound_speed(a[1])
        total += (distance / n) / self._get_sound_speed(b[1])
        for k in xrange(1, int(n)) :
            if a[0] != b[0] :
                x += math.cos(theta) * distance / n
            if a[1] != b[1] :
                y += math.sin(theta) * distance / n
            total += 2 * (distance / n) / self._get_sound_speed(y)
        return total * (distance / (2*n))

    def _get_snr(self, distance, target_strength) :
        loss = 10 * math.log(distance, 10) # cylindrical spreading
        #print '>', target_strength, distance, loss
        snr = self._source_level - 2*loss + target_strength - self._get_noise() - 10 * math.log(self._source_bw, 10)
        return snr

    def run(self) :
        self._edges = self._get_edges()
        while True :
            detects = self._edges[:]

            for entity in self.get_world().get_entities() :
                if entity.get_uid() == self.get_owner().get_uid() :
                    continue
                lat, lon, agl = self.get_owner().get_position()
                e_lat, e_lon, e_agl = entity.get_position()
                if e_agl <= 0 :
                    #TODO: use prop time
                    distance = math.sqrt(haver_distance(lat, lon, e_lat, e_lon)**2 + (agl - e_agl)**2) * 1000

                    snr = self._get_snr(distance, entity.get_parameter('sonar_level', 0))
                    bearing = int(bearing_from_pts(lat, lon, e_lat, e_lon))
                    if distance/1000 < detects[bearing][0] and snr >= self._min_snr :
                        detects[bearing] = [distance/1000, snr]

            merged_detects = {}
            for detector_start in range(0, 360, self._angles) :
                self._publish_data(SonarEvent(self.get_owner().get_uid(), detector_start, detects[detector_start:detector_start + self._angles]))
                #merged_detects[detector_start] = detects[detector_start:detector_start + self._angles]
                #print detector_start, ','.join(map(lambda e: str(e[0]) + '=' + str(e[1]), merged_detects[detector_start]))

#            self._publish_data(SonarEvent(self.get_owner().get_uid(), merged_detects))
            time.sleep(self._interval)
