#@Author Group 6
#Interface of the Payment Manager Module

from portobject import *

class OfferManager(PortObject):

    usernotifier_port = None # the port of the UserNotifier module
    ridemanager_port = None # the port of the RideManager module 
    """
    Manage the offers....
    we describe a few error code here:
    NEM : Not enough money
    NEP : Not enough places
    OK : it's cool eveything is fine
    RAA : request already agree by both on an other offer
    """
    def __init__(self,userNotifier,rideManager):
        """
        @pre:    db is an object that represents a DB on which we do SQL querries
                userNotifier is the port of the UserNotifier module
                rideManager  is the port of the RideManager module 
        @post:    OfferManager is init as a PortObect
                self.db=db
            self.usernotifier_port=userNotifier
            self.ridemananger_port=rideManager
        """
        self.usernotifier_port = userNotifier
        self.ridemanager_port = rideManager
        PortObject.__init__(self)
    
    def build_offer(requestID,proposalID):
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
        pass


    def driver_agree(offerID):
        """
        Change the DriverOk status for the offer into true if it doesn't exist an other offer such as the request is the same, and the status is bothAgree

        @pre:     offerID is the id of an existing offer in the db 
        @post:     if it doesn't exist an other offer such as the request is the same, and the status is bothAgree and there is enough seats in the car:
                    the DriveerOk for this offer is set to true
                else
                    the status for this offer is changed to cancelled
        @ret:    error Code in {OK,RAA,NEP}
        """
        pass

    def nondriver_agree(offer):
        """
        Change the nonDriverOk status for the offer into true if it doesn't exist an other offer such as the request is the same, and the status is bothAgree
        @post:     if it doesn't exist an other offer such as the request is the same, and the status is agreedByBoth and there is enough space in the car:
                    the nonDriverOk for this offer is set to true
                else
                    the status for this offer is changed to cancelled
        @ret:    error code in {OK,RAA,NEP}
        """
        pass

    def agree_by_both(offerID):
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
        pass

    def discarded(offerID):
        """
        the offer has been refused by a user
        @pre:    offerID exists in the db
        @post:    the offer status is set to 'discarded'
        """
        
    def routine(self, src, msg):
        """
        This is the message routine handler
        The message accepted are:
            - ('buildoffer',requestID,proposalID)
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
                    
        """
                    
            
            
            
            
            
            
