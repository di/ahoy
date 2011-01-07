import math

def haver_distance(lat1, lon1, lat2, lon2) :
    r = 6371
    dLat = float(math.radians(lat2-lat1))
    dLon = float(math.radians(lon2-lon1))
    a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon/2) * math.sin(dLon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return r * c

def lin_distance(lat1, lon1, alt1, lat2, lon2, alt2) :
    #TODO: add elevation data
    rad_earth = 6371 # km
    alt1 += rad_earth
    alt2 += rad_earth

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    
    x1 = alt1 * math.sin(lat1) * math.cos(lon1)
    y1 = alt1 * math.sin(lat1) * math.sin(lon1)
    z1 = alt1 * math.cos(lat1)

    x2 = alt2 * math.sin(lat2) * math.cos(lon2)
    y2 = alt2 * math.sin(lat2) * math.sin(lon2)
    z2 = alt2 * math.cos(lat2)

    dx = (x1 - x2)**2
    dy = (y1 - y2)**2
    dz = (z1 - z2)**2

    return math.sqrt(dx + dy + dz)

'''
def elevation(lat, lon) :
    import urllib, urllib2
    from xml.dom import minidom

    url = 'http://gisdata.usgs.gov/XMLWebServices/TNM_Elevation_Service.asmx/getElevation'
    
    values = {'X_Value' : lon,
    'Y_Value' : lat,
    'Elevation_Units' : 'meters',
    'Source_Layer' : '-1',
    'Elevation_Only' : '1', }
    
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = {'User-Agent' : user_agent}
    
    data = urllib.urlencode(values)
    get_url = url + '?' + data
    
    req = urllib2.Request(url=get_url, headers=headers)
    response = urllib2.urlopen(req)
    the_page = response.read()
    
    for entity, char in (('lt', '<'), ('gt', '>'), ('amp', '&')):
        the_page = the_page.replace('&%s;' % entity, char)

    the_page = the_page.replace('<string xmlns="http://gisdata.usgs.gov/XMLWebServices/">', '')
    the_page = the_page.replace('<?xml version="1.0" encoding="utf-8"?>\r\n', '')
    the_page = the_page.replace('</string>', '')
    the_page = the_page.replace('<!-- Elevation Values of -1.79769313486231E+308 (Negative Exponential Value) may mean the data source does not have values at that point.  --> <USGS_Elevation_Web_Service_Query>', '')
    
    dom = minidom.parseString(the_page)
    children = dom.getElementsByTagName('Elevation_Query')[0]
    
    elev = float(children.getElementsByTagName('Elevation')[0].firstChild.data)
    data_source = children.getElementsByTagName('Data_Source')[0].firstChild.data
    return elev
'''
