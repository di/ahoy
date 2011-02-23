import sys
import math
from numpy import *
from ahoy.util.geo import *

class Elevation :
    DATA_PATH = '../data/' # TODO: remove this
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
        f = open(Elevation.DATA_PATH + fn, 'rb')
        contents = f.read()
        f.close()
        data = flipud(((fromstring(string=contents, dtype='int16')).byteswap()).reshape(1201,1201))
        self._cached[fn] = data
        return data

    def get_height_at(self, lat, lon, degrees_per_index=3/3600.0) :
        height_array = self._get_height_array(self._get_filename(lat, lon))
        left = math.floor(lon)
        bot = math.floor(lat)
        dlat = lat - bot
        dlon = lon - left
        return height_array[int(dlat / degrees_per_index)][int(dlon / degrees_per_index)]

    def get_height_along(self, lat1, lon1, lat2, lon2, d=10/1000.0) :
        lat = lat1
        lon = lon1
        heights = []
        i = 0
        while True :
            y = math.sin(lon - lon2) * math.cos(lat2)
            x = math.cos(lat) * math.sin(lat2) - math.sin(lat) * math.cos(lat2) * math.cos(lon - lon2)
            bearing = math.degrees(math.atan2(y, x))

            R = 6378.1
            lat, lon = loc_from_bearing_dist(lat, lon, bearing, d)
            heights.append((lat, lon, d*i, self.get_height_at(lat, lon)))
            i += 1

            if haver_distance(lat, lon, lat2, lon2) < d :
                return heights

    def get_above(self, lat, lon, bearing, d=10/1000.0) :
        # Ignore the current position, start at *d*km away
        height0 = self.get_height_at(lat, lon)
        lat0, lon0 = lat, lon
        lat, lon = loc_from_bearing_dist(lat, lon, bearing, d)
        i = 0
        while True :
            R = 6378.1
            lat, lon = loc_from_bearing_dist(lat, lon, bearing, d)

            height = self.get_height_at(lat, lon)
            if height > height0 :
                # TODO: Could never terminate, but rarely.  Possibly fix.
                return lat, lon, haver_distance(lat0, lon0, lat, lon), height
            i += 1
