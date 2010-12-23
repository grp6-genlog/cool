#!/usr/bin/python
import math,datetime

""" Convert latitude and longitude to spherical coordinates in radians. """
def distance_on_unit_sphere(lat1, long1, lat2, long2):
    degrees_to_radians = math.pi/180.0
        
    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
        
    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
        
    # Compute spherical distance from spherical coordinates.
        
    # For two locations in spherical coordinates 
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) = 
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length
    
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )

    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    return arc

def get_distance((src_lat,src_lon),(dst_lat,dst_lon)):
    return distance_on_unit_sphere(src_lat,src_lon,dst_lat,dst_lon)*6368


"""
Return the time at the specified point of a list
points : list of RoutePoints
arrindex : index of specified point in the points list
deptime : departure time (datetime.datetime)
arrtime : arrival time (datetime.datetime)
"""
def get_time_at_point(points,arrindex,deptime,arrtime):
    total_dist=0.
    ride_dist=0.
    pos1 = points[0]
    for index in range(1,len(points)):
        dist = get_distance(pos1,points[index])
        total_dist+=dist
        if index<=arrindex:
            ride_dist+=dist
    return deptime + (arrtime-deptime) * int(ride_dist/total_dist)


""" convert a timedelta into seconds """
def total_seconds(td):
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6
