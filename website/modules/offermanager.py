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
        offer.status='pending'
        offer.driver_ok=False
        offer.non_driver_ok=False
        offer.pickup_point_lat=departure[0]
        offer.pickup_point_long=departure[1]
        offer.pickup_time = departure[2]
        offer.drop_point_lat=arrival[0]
        offer.drop_point_long=arrival[1]
        offer.drop_time = arrival[2]
        offer.total_fee=fee
        
        offer.save()


    def driver_agree(self,offerID):
        """
        Change the DriverOk status for the offer into true if it doesn't exist an other offer such as the request is the same, and the status is bothAgree

        @pre:     offerID is the id of an existing offer in the db 
        @post:     if it doesn't exist an other offer such as the request is the same, and the status is bothAgree and there is enough seats in the car:
                    the DriveerOk for this offer is set to true
                else
                    the status for this offer is changed to cancelled
        @ret:    error Code in {OK,RAA,NEP}
        """
        offer=Offer.objects.filter(id=offerID)
        if len(offer)==0:
            raise 'Try to agree an offer that not exists'
        offersAccepted=Offer.objects.filter(request=offer[0].request, status='A')
        if len(offersAccepted)!=0:
            discarded(offerID)
            return RAA
        proposal=Proposal.objects.filter(id=offer[0].proposal)
        if len(proposal)==0:
            raise 'Try to agree an offer that has no proposal'
        request=Request.objects.filter(id=offer[0].request)
        if len(request)==0:
            raise 'Try to agree an offer that has no request'
        if proposal.number_of_seats<request.nb_requested_seats:
            discarded(offerID)
            return NEP
        offer[0].driver_ok=True
        offer[0].save()
        if offer[0].non_driver_ok:
            return agree_by_both(offerID)
        return OK

    def nondriver_agree(self,offer):
        """
        Change the nonDriverOk status for the offer into true if it doesn't exist an other offer such as the request is the same, and the status is bothAgree
        @post:     if it doesn't exist an other offer such as the request is the same, and the status is agreedByBoth and there is enough space in the car:
                    the nonDriverOk for this offer is set to true
                else
                    the status for this offer is changed to cancelled
        @ret:    error code in {OK,RAA,NEP}"""
        offer=Offer.objects.filter(id=offerID)
        if len(offer)==0:
            raise 'Try to agree an offer that not exists'
        offersAccepted=Offer.objects.filter(request=offer[0].request, status='A')
        if len(offersAccepted)!=0:
            discarded(offerID)
            return RAA
        proposal=Proposal.objects.filter(id=offer[0].proposal)
        if len(proposal)==0:
            raise 'Try to agree an offer that has no proposal'
        request=Request.objects.filter(id=offer[0].request)
        if len(request)==0:
            raise 'Try to agree an offer that has no request'
        if proposal.number_of_seats<request.nb_requested_seats:
            discarded(offerID)
            return NEP
        offer[0].non_driver_ok=True
        offer[0].save()
        if offer[0].driver_ok:
            return agree_by_both(offerID)
        return OK

        

    def agree_by_both(self,offerID):
        """
        Try to change the status of the offer to agreedByBoth
        @pre:    offerID exists in the db
                the status of driverOk and nonDriverOk are both True
        @post:    if they are enough seats in the car and the nonDriver has enough money on his account
                        the offer status is set to agreedByBoth
            else
                if NEM:
                        nonDriverOK status is set to false
                    a msg is sent to UserNotifier :
                           ('newmsg','The offerID has a response. Not enough money to accept the ride. Please add money on your account.')
                the offer status is set to pending
        @ret:    error code in {OK,NEP,NEM}
        """
        offers=Offer.objects.filter(id=offerID)
        if len(offers)==0:
            raise "Try to accept an offer that doesn't exist"
        enoughSeats=False
        enoughMoney=False
        #Get the proposal, request linked to the offer
        requests=Request.objects.filter(id=offers[0].request)
        if len(requests)==0:
            raise 'Try to agree an offer where the request is invalid'
        proposals=Proposal.objects.filter(id=offers[0].proposal)
        if len(proposals)==0:
            raise 'Try to agree an offer where the profile is invalid'
        #Check enough money
        profiles=UserProfile.objects.filter(id=requests[0].user)
        if len(profiles)==0:
            raise 'Try to agree an offer where the profile is invalid'
        if profiles[0].account_balance>=offers[0].total_fee:
            enoughMoney=True
        #Check enough seats
        if proposals[0].number_of_seats>=requests[0].nb_requested_seats:
            enoughSeats=True
        if enoughSeats and enoughMoney:
            offers[0].status='A'
            offers[0].save()
            return OK
        elif not enoughSeats:
            discarded(offerID)
            return NEP
        else:
            offers[0].non_driver_ok=False
            send_to(self.userNotifier, ('newmsg', requests[0].user, 'The offerID has a response. Not enough money to accept the ride. Please add money on your account.'))
            return NEM
        send_to(self.rideManager, ('newacceptedride', offers[0].id))
        return OK

    def discarded(self,offerID):
        """
        the offer has been refused by a user
        @pre:    offerID exists in the db
        @post:    the offer status is set to 'discarded'
        """
        offers=Offer.objects.filter(id=offerID)
        if len(offers)==0:
            raise "Try to accept an offer that doesn't exist"
        offers[0].status='D'
        offers[0].save()
        
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
            try:
                self.build_offer(msg[1], msg[2], msg[3], msg[4])
            except:
                traceback.print_exc()
            
        elif msg[0]=='driveragree':
            try:
                ret = self.driver_agree(msg[1])
            except:
                threading.Thread(target = msg[3], args = (msg[4],)).start()
            else:
                if ret==OK:
                    threading.Thread(target = msg[2], args = (msg[4],)).start()
                elif ret==RAA:
                    threading.Thread(target = msg[3], args = (msg[4],RAA_MSG)).start()
                elif ret==NEP:
                    threading.Thread(target = msg[3], args = (msg[4],NEP_MSG)).start()
                
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
    dep = RoutePoints.object.get(id=departure)
    arr = RoutePoints.object.get(id=arrival)
    total=0.
    last = dep
    for index in range(dep.order+1,arr.order):
        tmp = RoutePoints.object.get(order=index,proposal=proposal)
        total+=get_distance((last.latitude,last.longitude),(tmp.latitude,tmp.longitude))
        last= tmp
    return total*proposal.money_per_km


