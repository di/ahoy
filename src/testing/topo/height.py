import sys
import math
from numpy import *

def get_filename(lat, lon) :
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

def get_height_array(fn) :
    f = open(fn, 'rb')
    contents = f.read()
    f.close()
    data = flipud(((fromstring(string=contents, dtype='int16')).byteswap()).reshape(1201,1201))
    return data

def get_height_at(lat, lon, height_array, degrees_per_index=3/3600.0) :
    left = math.floor(lon)
    bot = math.floor(lat)
    dlat = lat - bot
    dlon = lon - left
    print dlat, dlon, int(dlat / degrees_per_index), int(dlon / degrees_per_index)
    return height_array[int(dlat / degrees_per_index)][int(dlon / degrees_per_index)]

if __name__ == '__main__' :
    lat = float(sys.argv[1])
    lon = float(sys.argv[2])

    fn = get_filename(lat, lon)
    data = get_height_array(fn)
    height = get_height_at(lat, lon, data)

    print 'File Used: %s' % fn
    print 'Height: %s m' % height
'''
west_lat = float(sys.argv[2])
south_lon = float(sys.argv[3])

if west_lat < 0 :
    lat_change = -1
else :
    lat_change = 1

if south_lon < 0 :
    lon_change = -1
else :
    lon_change = 1

for i, row in enumerate(data) :
    for j, cell in enumerate(row) :
        print west_lat + lat_change*j*(3/3600.0), south_lon + lon_change*i*(3/3600.0), cell
'''
