import math

def haver_distance(lat1, lon1, lat2, lon2) :
    r = 6371
    dLat = float(math.radians(lat2-lat1))
    dLon = float(math.radians(lon2-lon1))
    a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon/2) * math.sin(dLon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return r * c

def sph_to_lin(lat, lon, agl) :
    rad_earth = 6371 # km
    agl += rad_earth

    lat = math.radians(lat)
    lon = math.radians(lon)
    
    x = agl * math.sin(lat) * math.cos(lon)
    y = agl * math.sin(lat) * math.sin(lon)
    z = agl * math.cos(lat)

    return x, y, z

def lin_to_sph(x, y, z) :
    rad_earth = 6371 # km
    r = math.sqrt(x**2 + y**2 + z**2)
    
    lat = math.acos(z/r)
    lon = math.atan(y/x)
    agl = r-rad_earth

    lat = math.degrees(lat)
    lon = math.degrees(lon)

    return lat, lon, agl

def lin_distance(lat1, lon1, alt1, lat2, lon2, alt2) :
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

def linear_to_degree(lat, lon, lat_km, lon_km) :
    # http://en.wikipedia.org/wiki/Geographic_coordinate_system#Expressing_latitude_and_longitude_as_linear_units
    km_per_lon = (math.pi / 180) * 6378137 * math.cos(0.99664719 * math.atan(lat)) / 1000
    km_per_lat = 111

    return lat_km/km_per_lat, lon_km/km_per_lon
