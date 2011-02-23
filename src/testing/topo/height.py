import sys
import math
from numpy import *
from ahoy.util.geo import *

class Elevation :
    def __init__(self) :
        self._cached = {}

    def _get_filename(self, lat, lon) :
        if lon < 0 :
            ew_str = 'W'
            bot = int(math.ceil(abs(lon)))
        else :
            ew_str = 'E'
            bot = int(lon)
        if lat < 0 :
            ns_str = 'S'
            left = int(math.ceil(abs(lat)))
        else :
            ns_str = 'N'
            left = int(lat)

        file = '%s%s%s%s.hgt' % (ns_str, str(left).rjust(2, '0'), ew_str, str(bot).rjust(3, '0'))
        return file

    def _get_height_array(self, fn) :
        if fn in self._cached.keys() :
            return self._cached[fn]
        f = open(fn, 'rb')
        contents = f.read()
        f.close()
        data = flipud(((fromstring(string=contents, dtype='int16')).byteswap()).reshape(1201,1201))
        self._cached[fn] = data
        return data

    def get_height_at(self, lat, lon, degrees_per_index=3/3600.0) :
        print lat, lon
        height_array = self._get_height_array(self._get_filename(lat, lon))
        left = math.floor(lon)
        bot = math.floor(lat)
        dlat = lat - bot
        dlon = lon - left
        return height_array[int(dlat / degrees_per_index)][int(dlon / degrees_per_index)]

    def _loc_from_bearing_dist(self, lat, lon, bearing, dist) :
        R = 6378.1
        lat = math.radians(lat)
        lon = math.radians(lon)
        bearing = math.radians(bearing)
        new_lat = math.degrees(math.asin(math.sin(lat)*math.cos(dist/R) + math.cos(lat)*math.sin(dist/R)*math.cos(bearing)))
        new_lon = math.degrees(lon + math.atan2(math.sin(bearing)*math.sin(dist/R)*math.cos(lat), math.cos(dist/R)-math.sin(lat)*math.sin(new_lat)))
        return new_lat, new_lon

    def get_height_along(self, lat1, lon1, lat2, lon2, d=10/1000.0) :
        lat = lat1
        lon = lon1
        heights = []
        while True :
            y = math.sin(lon - lon2) * math.cos(lat2)
            x = math.cos(lat) * math.sin(lat2) - math.sin(lat) * math.cos(lat2) * math.cos(lon - lon2)
            bearing = math.degrees(math.atan2(y, x))

            R = 6378.1 #km
            lat, lon = self._loc_from_bearing_dist(lat, lon, bearing, d)
            heights.append(self.get_height_at(lat, lon))

            if haver_distance(lat, lon, lat2, lon2) < d :
                return heights
