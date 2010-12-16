#@authors Group 6

from portobject import *

from django.contrib.auth.models import User
from website.profiles.models import UserProfile
from website.proposals.models import Proposal
from website.requests.models import Request
from website.offers.models import Offer
from website.rides.models import Ride
from math import sqrt
from utils import get_distance


    
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
        requests=Request.objects.filter(arrival_time__gt=infos.departure_time,nb_requested_seats__lt=infos.number_of_seats)
        for request in requests:
            found = False
            for offer in Offer.objects.filter(request=request.id):
                if Ride.objects.filter(offer=offer.id):
                    found=True
                    break
            if not found:
                d=None
                p=None
                pup=None
                dp=None
                i=0
                j=0
                c=0
                for rp in RoutePoints.object.filter(proposal=propID):
                    disdep = get_distance((request.departure_point_lat,request.departure_point_long),(rp.latitude,rp.longitude))
                    disarr = get_distance((request.arrival_point_lat,request.arrival_point_long),(rp.latitude,rp.longitude))
                    if(disdep<=rp.departure_range and (d==None or disdep<d)):
                        d=disdep
                        pup=(rp.latitude,rp.longitude)
                        i=c
                    if(disarr<= rp.arrival_range and p==None or disarr<p):
                        p=disarr
                        dp=(rp.latitude,rp.longitude)
                        j=c
                    c+=1
                            
                if pup!=None and dp!=None and i<j:
                    send_to(self.offermanager_port,('buildoffer',request.id,propID,pup,dp))


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
            infos=Request.objects.get(id=requestID)
            
            proposals=Proposal.objects.filter(departure_time__lt=infos.departure_time, number_of_seats__gte=infos.requested_seats)
            for proposal in proposals:
                d=None
                p=None
                pup=None
                dp=None
                i=0
                j=0
                c=0
                for rp in RoutePoints.object.filter(proposal=proposal.id):
                    disdep = get_distance((infos.departure_point_lat,infos.departure_point_long),(rp.latitude,rp.longitude))
                    disarr = get_distance((infos.arrival_point_lat,infos.arrival_point_long),(rp.latitude,rp.longitude))
                    if(disdep<=rp.departure_range and d==None or disdep<d):
                        d=disdep
                        pup=(rp.latitude,rp.longitude)
                        i=c
                    if(disarr<= rp.arrival_range and p==None or disarr<p):
                        p=disarr
                        dp=(rp.latitude,rp.longitude)
                        j=c
                    c+=1
                if pup!=None and dp!=None and i<j:
                    send_to(self.offermanager_port,('buildoffer',requestId,proposal.id,pup,dp))
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
