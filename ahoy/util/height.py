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
        height_array = self._get_height_array(self._get_filename(lat, lon))
        left = math.floor(lon)
        bot = math.floor(lat)
        dlat = lat - bot
        dlon = lon - left
        return height_array[int(dlat / degrees_per_index)][int(dlon / degrees_per_index)]

    def get_height_along(self, lat1, lon1, lat2, lon2, sample_dist_km=5/1000.0) :
        heights = []
        lat = math.radians(lat1)
        lon = math.radians(lon1)
        lat2 = math.radians(lat2)
        lon2 = math.radians(lon2)
        while True :
            y = math.sin(lon2 - lon) * math.cos(lat2)
            x = math.cos(lat) * math.sin(lat2) - math.sin(lat) * math.cos(lat2) * math.cos(lon2 - lon)
            bearing = math.atan2(y, x)

            R = 6378.1 #km
            lat = math.asin(math.sin(lat)*math.cos(sample_dist_km/R) + math.cos(lat)*math.sin(sample_dist_km/R)*math.cos(bearing))
            lon = lon + math.atan2(math.sin(bearing)*math.sin(sample_dist_km/R)*math.cos(lat), math.cos(sample_dist_km/R)-math.sin(lat)*math.sin(lat2))
            lat_d = math.degrees(lat)
            lon_d = math.degrees(lon)

            heights.append((lat_d, lon_d, self.get_height_at(lat_d, lon_d)))
            if haver_distance(lat, lon, lat2, lon2) < sample_dist_km :
                return heights

if __name__ == '__main__' :
    lat = float(sys.argv[1])
    lon = float(sys.argv[2])
    lat2 = float(sys.argv[3])
    lon2 = float(sys.argv[4])

    e = Elevation()

    heights = e.get_height_along(lat, lon, lat2, lon2)

    for i, data in enumerate(heights) :
        print i, data[0], data[1], data[2]
