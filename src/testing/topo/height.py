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
        return data

    def get_height_at(self, lat, lon, degrees_per_index=3/3600.0) :
        height_array = self._get_height_array(self._get_filename(lat, lon))
        left = math.floor(lon)
        bot = math.floor(lat)
        dlat = lat - bot
        dlon = lon - left
        return height_array[int(dlat / degrees_per_index)][int(dlon / degrees_per_index)]

    def get_height_along(self, lat1, lon1, lat2, lon2, sample_dist_km=5/1000.0) :
        while True :
            y = math.sin(lon2 - lon1) * math.cos(lat2)
            x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(lon2 - lon1)
            bearing = math.atan2(y, x)

            R = 6378.1 #km
            new_lat = math.degrees(math.asin(math.sin(lat1)*math.cos(d/R) + math.cos(lat1)*math.sin(sample_dist_km/R)*math.cos(bearing)))
            new_lon = math.degrees(lon1 + math.atan2(math.sin(bearing)*math.sin(sample_dist_km/R)*math.cos(lat1), math.cos(sample_dist_km/R)-math.sin(lat1)*math.sin(new_lat)))

            if haver_distance(new_lat, new_lon, lat2, lon2) < sample_dist_km :
                return distances

if __name__ == '__main__' :
    lat = float(sys.argv[1])
    lon = float(sys.argv[2])

    e = Elevation()

    height = e.get_height_at(lat, lon)

    print 'Height: %s m' % height
