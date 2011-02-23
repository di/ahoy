import Image
import sys
import zipfile
from numpy import *

f = open(sys.argv[1], 'rb')
contents = f.read()
f.close()
data = flipud(((fromstring(string=contents, dtype='int16')).byteswap()).reshape(1201,1201))
'''
west_lon = float(sys.argv[2])
south_lat = float(sys.argv[3])

if west_lon < 0 :
    lon_change = 1
else :
    lon_change = 1

if south_lat < 0 :
    lat_change = 1
else :
    lat_change = 1
'''
size = (1201,1201)
img = Image.new('RGB', size)
pixels = img.load()

for r, row in enumerate(data) :
    for c, cell in enumerate(row) :
        y = r
        x = c
        v = int(min(255, 255*(cell / 20.0)))
        if v <= 0 :
            pixels[x,len(row) - 1 - y] = (0,255,0)
        else :
            pixels[x,len(row) - 1 - y] = (v,v,v)
            #pixels[x,len(row) - 1 - y] = (255,255,255)

#        print '%s,%s %s (%s, %s = %s)' % (south_lat + lat_change*y*(3/3600.0), west_lon + lon_change*x*(3/3600.0), cell, x, y, v)
img.save('out.png')
