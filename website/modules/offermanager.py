#@Author Group 6
#Interface of the Offer Manager Module

from portobject import *
from website.offers.models import Offer
from website.requests.models import Request
from website.proposals.models import Proposal, RoutePoints
from google_tools_json import *
from utils import get_distance
import threading, traceback

OK=0
RAA=-1
NEP=-2

RAA_MSG="Request already agree by both on an other offer"
NEP_MSG="Not enough places"
NEM_MSG="Not enough money"

class OfferManager(PortObject):
    usernotifier_port=None # the port of the UserNotifier module
    ridemanager_port=None # the port of the RideManager module 
    """
    Manage the offers....
    we describe a few error code here:
    NEM : Not enough money
    NEP : Not enough places
    OK : it's cool eveything is fine
    RAA : request already agree by both on an other offer
    """
    def __init__(self, userNotifier,rideManager):
        """
        @pre:    db is an object that represents a DB on which we do SQL querries
                userNotifier is the port of the UserNotifier module
                rideManager  is the port of the RideManager module 
        @post:    OfferManager is init as a PortObect
                self.db=db
            self.usernotifier_port=userNotifier
            self.ridemananger_port=rideManager
        """
        PortObject.__init__(self)
        self.userNotifier=userNotifier
        self.rideManager=rideManager
    
    def build_offer(self,requestID,proposalID,departure,arrival):
        """
        Create a new offer in the database (a new entry in the offer table) for the request and the proposal.
        @pre: requestID is the ID of a request in db
              proposalID is the ID of a proposal in db
              It doesn't already exist an offer in the db for this couple requestID, proposalID
          
        @post:    A new offer is created in the db for the couple request proposal with the following states:
                        status = pending
                        DriverOk = false
                        nonDriverOk = false
        """
        proposals=Proposal.objects.filter(id=proposalID)
        
        if len(proposals)==0:
            raise "Try to build an offer from a proposal that doesn't exist"
        fee=compute_fee(proposals[0], departure[3], arrival[3])
        
        offer=Offer()
        offer.request=Request.objects.get(id=requestID)
        offer.proposal=Proposal.objects.get(id=proposalID)
        offer.status='P'
        offer.driver_ok=False
        offer.non_driver_ok=False
        offer.pickup_point_lat=departure[0]
        offer.pickup_point_long=departure[1]
        offer.pickup_time = departure[2]
        offer.drop_point_lat=arrival[0]
        offer.drop_point_long=arrival[1]
        offer.drop_time = arrival[2]
        offer.pickup_point = RoutePoints.objects.get(id=departure[3])
        offer.drop_point = RoutePoints.objects.get(id=arrival[3])
        offer.total_fee=fee
        offer.save()


    def driver_agree(self,(msg,offerID,callb_ok,callb_ko)):
        # ('driveragree',offerId,callb_ok,call_ko)
        offer=Offer.objects.get(id=offerID)
        offer.driver_ok=True
        offer.save()
        offersAccepted=Offer.objects.filter(request=offer.request, status='A')
        if len(offersAccepted)!=0:
            threading.Thread(target=callb_ko).start()
        else:
            if offer.non_driver_ok:
                route_points= RoutePoints.objects.filter(proposal=offer.proposal,order__gte=offer.pick_point.order,order__lte=offer.drop_point).order_by('order')
                point1=route_points[0]
                for point2 in route_points[1:]:
                    count = offer.request.nb_requested_seats
                    for offer2 in Offer.objects.filter(proposal=offer.proposal,status='A'):
                        if RoutePoints.filter(proposal=offer2.proposal,order=point1.order) and RoutePoints.filter(proposal=offer2.proposal,order=point2.order):
                            count+=offer2.request.nb_requested_seats
                        if count>offer.proposal.number_of_seats:
                            threading.Thread(target=callb_ko).start()
                    account = offer.request.user.account_balance
                
                for offer2 in Offer.objects.filter(status='A'):
                    if offer2.request.user.user == request.user:
                        account-=offer2.total_fee
                if account<0:
                    offer.non_driver_ok = False
                    offer.save()
                    send_to(self.userNotifier, ('newmsg', requests[0].user, 'The offerID has a response. Not enough money to accept the ride. Please add money on your account.'))
                    threading.Thread(target=callb_ko).start()
                else:
                    offer.status='A'
                    offer.save()
                    send_to(self.rideManager, ('newacceptedride', offers[0].id))
                    threading.Thread(target=callb_ok).start()
            else:
                threading.Thread(target=callb_ok).start()


    def nondriver_agree(self,(msg,offerID,callb_ok,callb_ko)):
        # ('nondriveragree',offerId,callb_ok,call_ko)
        offer=Offer.objects.get(id=offerID)
        offer.non_driver_ok=True
        offer.save()
        offersAccepted=Offer.objects.filter(request=offer.request, status='A')
        if len(offersAccepted)!=0:
            threading.Thread(target=callb_ko).start()
        else:
            if offer.driver_ok:
                route_points= RoutePoints.objects.filter(proposal=offer.proposal,order__gte=offer.pick_point.order,order__lte=offer.drop_point).order_by('order')
                point1=route_points[0]
                for point2 in route_points[1:]:
                    count = offer.request.nb_requested_seats
                    for offer2 in Offer.objects.filter(proposal=offer.proposal,status='A'):
                        if RoutePoints.filter(proposal=offer2.proposal,order=point1.order) and RoutePoints.filter(proposal=offer2.proposal,order=point2.order):
                            count+=offer2.request.nb_requested_seats
                        if count>offer.proposal.number_of_seats:
                            threading.Thread(target=callb_ko).start()
                    account = offer.request.user.account_balance
                for offer2 in Offer.objects.filter(status='A'):
                    if offer2.request.user.user == request.user:
                        account-=offer2.total_fee
                if account<0:
                    offer.non_driver_ok = False
                    offer.save()
                    send_to(self.userNotifier, ('newmsg', requests[0].user, 'The offerID has a response. Not enough money to accept the ride. Please add money on your account.'))
                    threading.Thread(target=callb_ko).start()
                else:
                    offer.status='A'
                    offer.save()
                    send_to(self.rideManager, ('newacceptedride', offers[0].id))
                    threading.Thread(target=callb_ok).start()
            else:
                threading.Thread(target=callb_ok).start()

    def discarded(self,offerID):
        """
        the offer has been refused by a user
        @pre:    offerID exists in the db
        @post:    the offer status is set to 'discarded'
        """
        offer=Offer.objects.get(id=offerID)
        offer.status='D'
        offer.save()
        
    def routine(self, src, msg):
        """
        This is the message routine handler
        The message accepted are:
            - ('buildoffer',requestID,proposalID, (departure_lat, departure_long), (arrival_lat, arrival_long))
            - ('driveragree',offerID, callbackProc)
            - ('nondriveragree',offerID, callbackProc)
            - ('refuseoffer',offerID,callbackProc)
        @pre:    for 'buildoffer' :
                        - requestID is a registered request in the db
                        - proposalID is a registered proposal in the db
                for 'driveragree' and 'nondriveragree':
                        - offerID is a registered offer in the db 
                        - callbackProc is a procedure
                            
        @post:    for 'buildoffer':
                    - post build_offer
                for 'driveragree':
                    - callbackProc(status, message) is called
                            status = True if the offer is correct (existing, waiting for answer)
                                False otherwise with a message of explaination
                    - post driver_agree
                    - if the driverOk = true and nonDriverOk = true
                            post agreeByBoth
                    - if agreeByBoth 
                            a message has been sent to the RideManager:
                            ('newacceptedride',offerID)

                for 'nondriveragree':
                    - callbackProc(status, message) is called
                            status = True if the offer is correct (existing, waiting for answer)
                                    False otherwise with a message of explaination
                    - post non_driver_agree
                    - if the driverOk = true and nonDriverOk = true
                        post agreeByBoth
                    - if agreeByBoth 
                            a message has been sent to the RideManager:
                            ('newacceptedride',offerID)
                for 'refuseoffer':
                    - callbackProc(status, message) is called
                            status = True if the offer is correct (existing, waiting for answer)
                                    False otherwise with a message of explaination
                    - post discarded
                for 'cancelrequest':
                    -                    
        """
        if msg[0]=='buildoffer':
            self.build_offer(msg[1], msg[2], msg[3], msg[4])
                        
        elif msg[0]=='driveragree':
            # ('driveragree',offerId,callb_ok,call_ko)
            ret = self.driver_agree(msg)
            
        elif msg[0]=='nondriver_agree':
            try:
                ret = self.nondriver_agree(msg[1])
            except:
                threading.Thread(target = msg[3], args = (msg[4],)).start()
            else:
                if ret==OK:
                    threading.Thread(target = msg[2], args = (msg[4],)).start()
                elif ret==RAA:
                    threading.Thread(target = msg[3], args = (msg[4],RAA_MSG)).start()
                elif ret==NEP:
                    threading.Thread(target = msg[3], args = (msg[4],NEP_MSG)).start()
                
        elif msg[0]=='refuseoffer':
            try:
                self.discarded(msg[1])
            except:
                threading.Thread(target = msg[3], args = (msg[4],)).start()
            else:
                threading.Thread(target = msg[2], args = (msg[4],)).start()
                    

"""
Compute the fee for the route between departure and arrival
@pre: proposalID is the id of the proposal, departure are the coordinates of departure point,
      arrival are the coordinates of arrival point, amount is the amount by kilometers, the host
      is connected to the internet
@post: the fee computed is returned
"""
def compute_fee(proposal, departure, arrival):
    dep = RoutePoints.objects.get(id=departure)
    arr = RoutePoints.objects.get(id=arrival)
    total=0.
    last = dep
    for index in range(dep.order+1,arr.order):
        tmp = RoutePoints.objects.get(order=index,proposal=proposal)
        total+=get_distance((last.latitude,last.longitude),(tmp.latitude,tmp.longitude))
        last= tmp
    return total*proposal.money_per_km


