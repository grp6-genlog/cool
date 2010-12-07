#@authors Group 6

from portobject import *

from django.contrib.auth.models import User
from website.profiles.models import UserProfile
from website.proposals.models import Proposal
from website.requests.models import Request

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
        try:
            infos=Proposal.objects.get(id=propID)
            requests=Request.objects.filter(departure_time__gt=infos.departure_time,nb_requested_seats__lt=infos.number_of_seats)
            for request in requests:
                if len(RoutePoints.object.filter(proposal=propID, latitude=request.departure_point_lat, longitude=request.departure_point_long))!=0 and len(RoutePoints.object.filter(proposal=propID,latitude=request.arrival_point_lat,longitude=request.arrival_point_long))!=0:
                    send_to(self.offermanager_port,('buildoffer',request.id,propID))
        except:
            print("Error : no or more than one proposal with the specified id had been found");

        

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
        try:
            infos=Proposal.objects.get(id=requestID)
            
            proposals=Proposal.objects.filter(departure_time__lt=infos.departure_time, number_of_seats__gte=infos.requested_seats)
            for proposal in proposals:
            
                if len(RoutePoints.object.filter(proposal=proposal.id, latitude=infos.departure_point_lat, longitude=infos.departure_point_long))==0 and len(RoutePoints.object.filter(proposal=proposal.id,latitude=infos.arrival_point_lat,longitude=infos.arrival_point_long))==0:
                    send_to(self.offermanager_port,('buildoffer',requestID,proposal.id))
                    
        except:
            print("Error on match request\n")


              
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
