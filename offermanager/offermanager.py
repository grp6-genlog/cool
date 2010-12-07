#@Author Group 6
#Interface of the Payment Manager Module

from portobjectIF import *
from offers.models import Offer

OK=0
RAA=-1
NEP=-2

RAA_MSG="Request already agree by both on an other offer"
NEP_MSG="Not enough places"
NEM_MSG="Not enough money"

class OfferManager(PortObject):
	db=None #stand for data base
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
	def __init__(self,db,userNotifier,rideManager):
		"""
		@pre:	db is an object that represents a DB on which we do SQL querries
				userNotifier is the port of the UserNotifier module
				rideManager  is the port of the RideManager module 
		@post:	OfferManager is init as a PortObect
		        self.db=db
			self.usernotifier_port=userNotifier
			self.ridemananger_port=rideManager
		"""
		self.db=db
		self.userNotifier=userNotifier
		self.rideManager=rideManager
	
	def build_offer(requestID,proposalID):
		"""
		Create a new offer in the database (a new entry in the offer table) for the request and the proposal.
		@pre: requestID is the ID of a request in db
		      proposalID is the ID of a proposal in db
		      It doesn't already exist an offer in the db for this couple requestID, proposalID
		  
		@post:	A new offer is created in the db for the couple request proposal with the following states:
						status = pending
						DriverOk = false
						nonDriverOk = false
		"""
		offer=Offer(request=requestID, proposal=proposalID, status='P', driver_ok=False, nondriver_ok=False)
		offer.save()


	def driver_agree(offerID):
		"""
		Change the DriverOk status for the offer into true if it doesn't exist an other offer such as the request is the same, and the status is bothAgree

		@pre: 	offerID is the id of an existing offer in the db 
		@post: 	if it doesn't exist an other offer such as the request is the same, and the status is bothAgree and there is enough seats in the car:
					the DriveerOk for this offer is set to true
				else
					the status for this offer is changed to cancelled
		@ret:	error Code in {OK,RAA,NEP}
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
		if offer[0].non_driver_ok:
			return agree_by_both(offerID)
		return OK

	def nondriver_agree(offer):
		"""
		Change the nonDriverOk status for the offer into true if it doesn't exist an other offer such as the request is the same, and the status is bothAgree
		@post: 	if it doesn't exist an other offer such as the request is the same, and the status is agreedByBoth and there is enough space in the car:
					the nonDriverOk for this offer is set to true
				else
					the status for this offer is changed to cancelled
		@ret:	error code in {OK,RAA,NEP}"""
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
		if offer[0].driver_ok:
			return agree_by_both(offerID)
		return OK

		

	def agree_by_both(offerID):
		"""
		Try to change the status of the offer to agreedByBoth
		@pre:	offerID exists in the db
				the status of driverOk and nonDriverOk are both True
		@post:	if they are enough seats in the car and the nonDriver has enough money on his account
		                the offer status is set to agreedByBoth
			else
				if NEM:
				        nonDriverOK status is set to false
					a msg is sent to UserNotifier :
					       ('newmsg','The offerID has a response. Not enough money to accept the ride. Please add money on your account.')
				the offer status is set to pending
		@ret:	error code in {OK,NEP,NEM}
		"""
		pass

	def discarded(offerID):
		"""
		the offer has been refused by a user
		@pre:	offerID exists in the db
		@post:	the offer status is set to 'discarded'
		"""
		
	def routine(self, src, msg):
		"""
		This is the message routine handler
		The message accepted are:
			- ('buildoffer',requestID,proposalID)
			- ('driveragree',offerID, callbackProc)
			- ('nondriveragree',offerID, callbackProc)
			- ('refuseoffer',offerID,callbackProc)
		@pre:	for 'buildoffer' :
		                - requestID is a registered request in the db
				        - proposalID is a registered proposal in the db
			    for 'driveragree' and 'nondriveragree':
			            - offerID is a registered offer in the db 
				        - callbackProc is a procedure
					        
		@post:	for 'buildoffer':
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
		if msg[0]=='buildoffer':
			build_offer(msg[1], msg[2])
			callbackProc(True, "")
		elif msg[0]=='driveragree':
			ret=driver_agree(msg[1])
			if ret==OK:
				callbackProc(True, "")
			elif ret==RAA:
				callbackProc(False, RAA_MSG)
			elif ret==NEP:
				callbackProc(False, NEP_MSG)
		elif msg[0]=='nondriver_agree':
			nondriver_agree(msg[1])
			if ret==OK:
				callbackProc(True, "")
			elif ret==RAA:
				callbackProc(False, RAA_MSG)
			elif ret==NEP:
				callbackProc(False, NEP_MSG)
		elif msg[0]=='refuseoffer':
			discarded(msg[1])
			callbackProc(True, "")

"""
Get an offer from the database that correspond to offerId
@pre: DB is initialized and is a SQL database
@post: the database is unchanged
"""
def get_offer_from_database(DB, offerId):
	pass
			
					
			
			
			
			
			
			
