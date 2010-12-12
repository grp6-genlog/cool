#!/usr/bin/python

import urllib
import json

DIRECTION_URL="http://maps.googleapis.com/maps/api/directions/json"
END_URL="sensor=false"

OK=0
ERROR=-1
ACCESS_DENIED=-2

"""
Note about the specification of the location
--------------------------------------------

The string used to specify a location can have several formats :
- 'Lat, Long' where Lat is the latitude and Long is the longitude (ex. '50.6654700,4.5668400')
- 'Location_name' (ex. 'Louvain-La-Neuve')
- 'Address' (ex. '2,Place+Sainte-Barbe,1348,Louvain-La-Neuve')
Warning : The spaces must be replaced by '+'
"""


"""
Get the destination from origin to destination passing through
checkpoints
@pre : origin and destination are strings
       checkpoints is a list of strings
@post : the distance is returned (in meters). If the locations are unknown -1 is returned
"""
def distance_origin_dest(origin, destination, checkpoints):
    doc=get_json_direction_doc(origin, destination, checkpoints)
    parsed_doc=json.loads(doc.read())
    if check_status(parsed_doc)==OK:
        return int(get_distance_from_doc(parsed_doc))
    else:
        return -1

"""
Get the distance from an json_doc
@pre : json_doc must be the json responsed by Google Maps, it must already parsed and
     the status is OK
@post : the distance (in meters) is extracted from the json_doc
"""
def get_distance_from_doc(json_doc):
    routes=json_doc['routes']
    if len(routes)==0:
        return -1
    legs=routes[0]['legs']
    if len(legs)==0:
        return -1
    return legs[-1]['distance']['value']

"""
Get the json_doc from Google maps web service
@pre : origin and destination are strings
       checkpoints is a list of strings
@post : the request has been sent and received. The json response is returned
"""
def get_json_direction_doc(origin, destination, checkpoints, print_url=False):
    #First part of the url with origin and destination
    url="%s?origin=%s&destination=%s&" % (DIRECTION_URL, origin, destination)
    #Adds the chekpoints in the request
    if len(checkpoints)!=0:
        url+="&waypoints="
    i=0
    for loc in checkpoints:
        if i==0:
            url+=loc
        else:
            url+="|"+loc
        i+=1
    #End part of the url
    url+="&"+END_URL
    if print_url:
        print url
    #Get the web service
    data=urllib.urlopen(url)
    return data

"""
Check the status of the json_doc
@pre : json_doc is an json response from Google Maps and is already parsed
@post : the status of the json_doc is returned
"""
def check_status(json_doc):
    status=json_doc['status']
    if status=="OK":
        return OK
    elif status=="ACCESS_DENIED":
        return ACCESS_DENIED
    else:
        return ERROR

if __name__=='__main__':
    print distance_origin_dest("Grez-Doiceau", "Louvain-La-Neuve", ["Brussels", "Antwerp"])

