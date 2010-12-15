# @Author Group 6
# Interface of the RequestRecorder module

from portobject import *
from website.offers.models import Offer
from website.rides.models import Ride
from website.proposls.models import Proposal
from webstie.requests.models import Request

class RideManager(PortObject):

    usernotifier_port=None # the communication port of UserNotifier
    tracker_port=None # the communication port of Tracker
    paymentmanager_port=None # the communication port of PaymentManager
    evaluationmanager_port=None # the communication port of EvaluationManager
    
    def __init__(self,usernotifier_port,tracker_port,paymentmanager_port,evaluationmanager_port):
        """
        Initialize the DB and all known modules ports of the RequestRecorder.
        @pre usernotifier_port is the UserNotifier module port (a Queue)
             tracker_port is the Tracker module port (a Queue)
             paymentmanager_port is the PaymentManager module port (a Queue)
             evaluationmanager_port is the evaluationmanager module port (a Queue)

        @post self.usernotifier_port = usernotifier_port
              self.tracker_port = tracker_port
              self.paymentmanager_port = paymentmanager_port
              self.evaluationmanager_port = evaluationmanager_port
        """
        self.usernotifier_port = usernotifier_port
        self.tracker_port = tracker_port
        self.paymentmanager_port = paymentmanager_port
        self.evaluationmanager_port = evaluationmanager_port
        PortObject.__init__(self)
        
    def buildinstructions(self,msg):
        """
        The ('newacceptedride',offerID) message treatement.
        @pre : DB is initialized and is the SQL database
               self.usernotifier_port is the UserNotifier module port (a Queue)
               self.tracker_port is the Tracker module port (a Queue)
               self.paymentmanager_port is the PaymentManager module port (a Queue)
               self.evaluationmanager_port is the evaluationmanager module port (a Queue)
               
               offerID is the id of an offer in the database.
      
        @post : the instruction is built from the specified offer and is added to the DB (in the instruction table).
                two messages are sent to UserNotifier through its port (usernotifier_port):
                  ('newmsg',nondriverID,'You've got a ride for request requestID. Please visit your account for further information.')
                  ('newmsg',driverID,'You've got a shared ride for proposalID. Please visit your account for further information.')
                a thread is run to send the following differed message to Tracker at rideTime - 30min:
                  ('startride',instructionID,closeRide(),cancelRide()) with instructionID the id of the request in the DB's table. and closeRide,cancelRide callback functions = lambda close_ride(self,instructionID).
                a thread is run to send the following differed message to RideManager at rideTime:
                  ('startevaluation',instructionID) with instructionID the id of the request in the DB's table.
        """
        offer=Offer.object.get(id=msg[1])
        if offer==None:
            raise "There doesn't exist an offer for %d" % msg[1]
        proposal=Proposal.object.get(id=offer.proposal)
        request=Request.object.get(id=offer.request)
        if proposal==None or request==None:
            raise "There doesn't exist a proposal or a request for the offer %d" % msg[1]
        ride=Ride(offer=msg[1], ride_started=False)
        ride.save()
        self.send_to(usernotifier_port, ('newmsg', proposal.user, "You've got a shared ride for proposal %d. Please visit your account for further information." % proposal.id))
        self.send_to(usernotifier_port, ('newmsg', request.user, "You've got a shared ride for request %d. Please visit your account for further information." % request.id))

        #compute ridetime-30 in seconds
        start=proposal.departure_time
        today=datetime.today()
        delta1=timedelta(minutes=30)
        time_to_send=start-delta1
        ridetime_minus_30=time_to_send-today
        if ridetime_minus_30.microseconds<0 or ridetime_minus_30.seconds<0 or ridetime_minus_30.days<0:
            raise 'The time to send the message is negative'
        sec1=ridetime_minus_30.seconds+ridetime_minus_30.days*86400

        #compute ridetime in seconds
        delta2=timedelta()
        ridetime=start-delta2
        if ridetime.microseconds<0 or ridetime.seconds<0 or ridetim.days<0:
            raise 'The time to send the message is negative'
        sec2=ridetime.seconds+ridetime.days*86400

        delay1=delayAction(sec1, self.send_to, (tracker_port, ('startride', ride.id, self.close_ride, self.cancel_ride)))
        delay2=delayAction(sec2, self.send_to, (evaluationmanager_port, ('startevaluation', proposal.user, ride.id)))
        delay3=delayAction(sec2, self.send_to, (evaluationmanager_port, ('startevaluation', request.user, ride.id)))
        delay1.start()
        delay2.start()
        delay3.start()

    def close_ride(self,instructionID):
        """
        The ride is done, send payment and modify db.
        @pre : DB is initialized and is the SQL database
               self.usernotifier_port is the UserNotifier module port (a Queue)
               self.tracker_port is the Tracker module port (a Queue)
               self.paymentmanager_port is the PaymentManager module port (a Queue)
               self.evaluationmanager_port is the evaluationmanager module port (a Queue)
               
               instructionID is the id of an instruction in the database.

        @post : DB's instruction status is modified at 'done'
                a message is sent to the PaymentManager to pay the fee:
                   ('payfee',instructionID)
        """
        ride=Ride.objects.get(id=instructionID)
	if ride==None:
		raise 'There is no instruction for %d' % instructionID
	offer=Offer.object.get(id=ride.offer)
	if offer==None:
		raise 'There is no offer for this instruction'
	offer.status('F')
	offer.save()
	self.send_to(evaluationmanager_port, ('payfee', instructionID))

    def cancel_ride(self,instructionID):
        """
        The ride is cancelled, returns payment and modify db.
        @pre : DB is initialized and is the SQL database
               self.usernotifier_port is the UserNotifier module port (a Queue)
               self.tracker_port is the Tracker module port (a Queue)
               self.paymentmanager_port is the PaymentManager module port (a Queue)
               self.evaluationmanager_port is the evaluationmanager module port (a Queue)
               
               instructionID is the id of an instruction in the database.

        @post : DB's instruction status is modified at 'done'
                a message is sent to the PaymentManager to pay the fee:
                   ('returnfee',instructionID)
                a message is sent for both user saying that the ride has been cancelled to UserNotifier:
                   ('newmsg',usersID,"The ride instructionID has been cancelled.")
        """
        ride=Ride.objects.get(id=instructionID)
	if ride==None:
		raise 'There is no instruction for %d' % instructionID
	offer=Offer.object.get(id=ride.offer)
	if offer==None:
		raise 'There is no offer for this instruction'
	nondriver=Request.object.get(id=offer.request)
	driver=Proposal.object.get(id=offer.proposal)
	if nondriver==None or driver==None:
		raise 'There is a problem with the users'
	offer.status('F')
	offer.save()
	self.send_to(evaluationmanager_port, ('returnfee', instructionID)
	self.send_to(usernotifier_port, ('newmsg', nondriver.user, 'The ride %d has been cancelled' % instructionID))
	self.send_to(usernotifier_port, ('newmsg', driver.user, 'The ride %d has been cancelled' % instructionID))

    def routine(self,src,msg):
        """
        The msg treatement routine.
        The only acceptable messages are ('cancelride',instructionID,successCancelRide,failureCancelRide)
                                         ('newacceptedride',offerID)
        
        for 'cancelride', see self.cancel_ride(instructionID) if the request is valid 
                (ride existing, pending,...) in which case successCancelRide is called
                otherwise failureCancelRide is called with an optional explanation message
        )
        for 'newacceptedride', see self.buildinstruction msg
        """
        if msg[0]=='cancelride':
		res=self.cancel_ride(msg[1])
		if res==0:
			successCancelRide()
		else:
			failureCancelRide('The ride cannot be canceled')
	elif msg[0]=='newacceptedride':
		self.buildinstruction(msg)

#timer description
class delayAction:
	def __init__(self, delay, fun, arg):
		self.delay = delay
		self.fun = fun
		self.arg = arg
	def start(self):
		self.t = Timer(self.delay,self.fun,self.arg)
		self.t.start()
	def cancel(self):
		self.t.cancel()
		self.t.join()
	def restart(self):
		self.cancel()
		self.t = Timer(self.delay,self.fun,self.arg)
		self.t.start()
