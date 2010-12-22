#@authors Group 6

from portobject import *

from django.contrib.auth.models import User
from website.profiles.models import UserProfile
from website.proposals.models import Proposal, RoutePoints
from website.requests.models import Request
from website.offers.models import Offer
from website.rides.models import Ride
from math import sqrt
from utils import get_distance,get_time_at_point, total_seconds


    
"""
This is the interface for the FindPair port object. 
This is the classe that will be responsible to find matches between proposals
and offers.
"""
class FindPair(PortObject): 
    offermanager_port=None # the OfferManager module's port

    
    def __init__(self,offerman):
        """
            Initialisation of self DB and offermananger_port
            Pre : the instance of FindPair is not already initialized
                  offerman is the OfferManager module's port
            Post : the instance is initialized :
                       self.offermanager_port = offerman
                       
        """
        PortObject.__init__(self)
        self.offermanager_port = offerman
                
    def match_proposal(self,propID):
        """
        This operation try to match the specified proposal with each request of the DB
        
        @pre : DB has been initialized and is the SQL database
               offermanager_port has been initialized and is the port of the OfferManager module
               
               propId is the id of a proposal in the database
               
        @post : DB has not been modified.
                for each request matching the specified proposal, a message is sent to OfferManager through its port:
                    ('buildoffer',requestID,proposalID) with requestID, the database ID of the matching request
        """
        infos=Proposal.objects.get(id=propID)
        requests=Request.objects.filter(nb_requested_seats__lte=infos.number_of_seats, status='P')
        print "len req:"+str(len(requests))
        for request in requests:
            found = False
            for offer in Offer.objects.filter(request=request):
                if Ride.objects.filter(offer=offer):
                    found=True
                    break
            if not found:
                route_points = RoutePoints.objects.filter(proposal=infos).order_by('order')
                valid_pair = list()
                for i in xrange(len(route_points)-1):
                    if get_distance((request.departure_point_lat,request.departure_point_long),(route_points[i].latitude,route_points[i].longitude))<request.departure_range:
                        for j in range(i+1,len(route_points)):
                            if get_distance((request.arrival_point_lat,request.arrival_point_long),(route_points[j].latitude,route_points[j].longitude))<request.arrival_range:
                                valid_pair.append((i,j))
                for (i,j) in valid_pair:
                    #delete all not in time arrival
                    if total_seconds(abs(get_time_at_point([(r.latitude,r.longitude) for r in route_points],j,infos.departure_time,infos.arrival_time)-request.arrival_time)) < request.max_delay:
                        self.send_to(self.offermanager_port, ('buildoffer',
                                     request.id,
                                     infos.id, 
                                     (
                                        route_points[i].latitude,
                                        route_points[i].longitude,
                                        get_time_at_point([(r.latitude,r.longitude) for r in route_points], 
                                                            i,
                                                            infos.departure_time,
                                                            infos.arrival_time),
                                        route_points[i].id
                                     ),
                                     (
                                        route_points[j].latitude,
                                        route_points[j].longitude,
                                        get_time_at_point([(r.latitude,r.longitude) for r in route_points],
                                                            j,
                                                            infos.departure_time,infos.arrival_time),
                                        route_points[j].id
                                      )
                                ))

    def match_request(self,requestID):
        """
        This operation try to match the specified proposal with each request of the DB
        
        @pre : DB has been initialized and is the SQL database
               offermanager_port has been initialized and is the port of the OfferManager module
               
               requestId is the id of a request in the database
               
        @post : DB has not been modified.
                for each proposal matching the specified request, a message is sent to OfferManager through its port:
                    ('buildoffer',requestID,proposalID) with proposalID, the database ID of the matching proposal
        """
        request=Request.objects.get(id=requestID)
        proposals=Proposal.objects.filter(number_of_seats__gte=request.nb_requested_seats,status='P')
        for infos in proposals:
            route_points = RoutePoints.objects.filter(proposal=infos).order_by('order')
            valid_pair = list()
            for i in xrange(len(route_points)-1):
                if get_distance((request.departure_point_lat,request.departure_point_long),(route_points[i].latitude,route_points[i].longitude))<request.departure_range:
                
                    for j in range(i+1,len(route_points)):
                        if get_distance((request.arrival_point_lat,request.arrival_point_long),(route_points[j].latitude,route_points[j].longitude))<request.arrival_range:
                            valid_pair.append((i,j))
                            
            for (i,j) in valid_pair:
                #delete all not in time arrival
                if total_seconds(abs(get_time_at_point([(r.latitude,r.longitude) for r in route_points],j,infos.departure_time,infos.arrival_time)-request.arrival_time)) < request.max_delay:
                    self.send_to(self.offermanager_port,('buildoffer',
                                                          requestID,
                                                          infos.id,
                                                          ( route_points[i].latitude,
                                                            route_points[i].longitude,
                                                            get_time_at_point([(r.latitude,r.longitude) for r in route_points],
                                                                              i,
                                                                              infos.departure_time,infos.arrival_time),
                                                            route_points[i].id
                                                          ),
                                                          ( route_points[j].latitude,
                                                            route_points[j].longitude,
                                                            get_time_at_point([(r.latitude,r.longitude) for r in route_points],
                                                                              j,
                                                                              infos.departure_time,
                                                                              infos.arrival_time),
                                                            route_points[j].id
                                                          )
                                                      ))


              
    def routine(self,src,msg):
        """
            This is the operation that will read msg type and dispatch
            in consequence through match_request or match_proposal.

            Pre : msg  is of the type :
                    ('newrequest',requestID)
                  or
                    ('newproposal',proposalID)
            Post : match_request (if 'newrequest') 
                   or match_proposal (if 'newproposal') is executed
        """

        (st,ide)=msg
        if(st=='newproposal'):
            self.match_proposal(ide)
        elif(st=='newrequest'):
            self.match_request(ide)
        else:
            print "You gave a bad request name to FindPair.\n"
