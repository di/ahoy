#!/usr/bin/python
import sys
import urllib2
import subprocess
l = sys.argv[1]
response = urllib2.urlopen('http://dds.cr.usgs.gov/srtm/version2_1/SRTM3/North_America/%s.zip' % l.strip())
data = response.read()
w = open(l.strip() + '.zip', 'wb')
w.write(data)
w.close()
subprocess.Popen(['unzip', l.strip() + '.zip'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
subprocess.Popen(['rm', l.strip() + '.zip']).communicate()
