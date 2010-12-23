# @Author Group 6
# Interface of the RequestRecorder module

from portobject import *
from website.offers.models import Offer
from website.rides.models import Ride
from website.proposals.models import Proposal
from website.requests.models import Request
from datetime import *
import threading, json


class RideManager(PortObject):

    usernotifier_port=None # the communication port of UserNotifier
    tracker_port=None # the communication port of Tracker
    paymentmanager_port=None # the communication port of PaymentManager
    evaluationmanager_port=None # the communication port of EvaluationManager
    
    def __init__(self,usernotifier_port,tracker_port,paymentmanager_port,evaluationmanager_port, global_address_cache):
        """
        Initialize all known modules ports of the RequestRecorder.
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
        self.global_address_cache = global_address_cache
        PortObject.__init__(self)
        
    def buildinstructions(self,msg):
        """
        The ('newacceptedride',) message treatement.
        @pre : self.usernotifier_port is the UserNotifier module port (a Queue)
               self.tracker_port is the Tracker module port (a Queue)
               self.paymentmanager_port is the PaymentManager module port (a Queue)
               self.evaluationmanager_port is the evaluationmanager module port (a Queue)
               
               offerID is the id of an offer in the database.
      
        @post : the instruction is built from the specified offer and is added to the DB (in the instruction table).
                two messages are sent to UserNotifier through its port (usernotifier_port):
                  ('newmsg', nondriverID, msg1)
                  ('newmsg',driverID,msg2)
                msg1 and msg2 are text message containing the ride information
                a thread is run to send the following differed message to Tracker at rideTime - 30min:
                  ('startride',instructionID,closeRide(),cancelRide()) with instructionID the id of the request in the DB's table. and closeRide,cancelRide callback functions = lambda close_ride(self,instructionID).
                a thread is run to send the following differed message to RideManager at rideTime:
                  ('startevaluation',instructionID) with instructionID the id of the request in the DB's table.
        """

        offer=Offer.objects.get(id=msg[1])
        ride=Ride(offer=offer, ride_started=False)
        ride.save()
        
        pickup_point = self.global_address_cache.get_address((ride.offer.pickup_point.latitude,ride.offer.pickup_point.longitude))
        drop_point = self.global_address_cache.get_address((ride.offer.drop_point.latitude,ride.offer.drop_point.longitude))
             
        message_for_proposal="You have ride with "+offer.request.user.user.first_name +" "+offer.request.user.user.last_name+"\n"
        message_for_proposal+="The phone number of non-driver is: "+offer.request.user.phone_number +"\n"
        message_for_proposal+="The pick up point is at "+pickup_point+"\n"
        message_for_proposal+="The ride start at: "+str(ride.offer.pickup_time)+"\n"
        message_for_proposal+="The drop point is at "+drop_point+"\n"
        message_for_proposal+="The drop time is: "+str(offer.drop_time)+"\n"
        message_for_proposal+="Please visit your account for further information"

        message_for_request="You have ride with "+offer.proposal.user.user.first_name +" "+offer.proposal.user.user.last_name+"\n"
        message_for_request+="The phone number of driver is: "+offer.proposal.user.phone_number +"\n" 
        message_for_request+="The pick up point is at "+pickup_point+"\n"
        message_for_request+="The ride start at: "+str(ride.offer.pickup_time)+"\n"
        message_for_request+="The drop point is at "+drop_point+"\n"
        message_for_request+="The drop time is"+str(offer.drop_time)+"\n"
        message_for_request+="Please visit your account for further information"
                            
                       
        self.send_to(self.usernotifier_port, ('newmsg', offer.proposal.user.id, message_for_proposal))
        
        self.send_to(self.usernotifier_port, ('newmsg', offer.request.user.id, message_for_request))

        # compute ridetime-30 in seconds
        start = offer.proposal.departure_time # datetime
        today = datetime.now() # datetime
        
        half_hour = timedelta(minutes=30) # delta
        time_to_send = start - half_hour # datetime
        
        
        half_hour_before = (today-time_to_send).seconds + (today-time_to_send).days*86400
        until_ride = (today-start).seconds + (today-start).days*86400
        
        if today>time_to_send:
            self.send_to(self.tracker_port,('startride', ride.id,lambda: self.close_ride(ride.id),lambda: self.cancel_ride(ride.id)))
            
        else:
            delay1=delayAction(half_hour_before, self.send_to, (self.tracker_port, ('startride', ride.id,lambda: self.close_ride(ride.id),lambda: self.cancel_ride(ride.id))))
            delay1.start()
        
        delay2=delayAction(until_ride, self.send_to, (self.evaluationmanager_port, ('startevaluation', offer.proposal.user.id, ride.id)))
        delay3=delayAction(until_ride, self.send_to, (self.evaluationmanager_port, ('startevaluation', offer.request.user.id, ride.id)))
        
        delay2.start()
        delay3.start()

    def close_ride(self,rideID):
        """
        The ride is done, send payment and modify db.
        @pre : self.usernotifier_port is the UserNotifier module port (a Queue)
               self.tracker_port is the Tracker module port (a Queue)
               self.paymentmanager_port is the PaymentManager module port (a Queue)
               self.evaluationmanager_port is the evaluationmanager module port (a Queue)
               
               rideID is the id of a ride in the database.

        @post : DB's offer status is modified at 'F'
                a message is sent to the PaymentManager to pay the fee:
                   ('payfee',rideID)
        """
        ride=Ride.objects.get(id=rideID)
        offer=Offer.objects.get(id=ride.offer.id)
        offer.status = 'F'
        offer.save()
        self.send_to(self.paymentmanager_port, ('payfee', rideID))

    def cancel_ride(self, rideID):
        """
        The ride is cancelled, returns payment and modify db.
        @pre : self.usernotifier_port is the UserNotifier module port (a Queue)
               self.tracker_port is the Tracker module port (a Queue)
               self.paymentmanager_port is the PaymentManager module port (a Queue)
               self.evaluationmanager_port is the evaluationmanager module port (a Queue)
               
               rideID is the id of a ride in the database.

        @post : DB's offer status is modified at 'F'
                a message is sent to the PaymentManager to pay the fee:
                   ('returnfee',rideID)
                a message is sent for both user saying that the ride has been cancelled to UserNotifier:
                   ('newmsg',usersID, msg)
                msg contains the information about the ride
        """
        ride=Ride.objects.get(id=rideID)
        if ride.ride_started:
            return 0

        ride.offer.status = 'C'
        ride.offer.save()        

        pickup_point = self.global_address_cache.get_address((ride.offer.pickup_point.latitude,ride.offer.pickup_point.longitude))
        drop_point = self.global_address_cache.get_address((ride.offer.drop_point.latitude,ride.offer.drop_point.longitude))
        
        
        message_for_proposal="Your ride with "+ride.offer.request.user.user.first_name +" "+ride.offer.request.user.user.last_name+" "+"is cancelled"+"\n"
        message_for_proposal+="Information of ride: "+"\n"
        message_for_proposal+="The pick up point was at "+pickup_point+"\n"
        message_for_proposal+="The ride started at: "+str(ride.offer.pickup_time)+"\n"
        message_for_proposal+="The drop point was at "+drop_point+"\n"
        message_for_proposal+="The drop time was at "+str(ride.offer.drop_time)+"\n"
        message_for_proposal+="Please visit your account for further information"

        message_for_request="You have ride with "+ride.offer.proposal.user.user.first_name +" "+ride.offer.proposal.user.user.last_name+" "+"is cancelled"+"\n"
        message_for_request+="Information of ride: "+"\n"
        message_for_request+="The pick up point was at "+pickup_point+"\n"
        message_for_request+="The ride started at: "+str(ride.offer.pickup_time)+"\n"
        message_for_request+="The drop point was at "+drop_point+"\n"
        message_for_request+="The drop time was"+str(ride.offer.drop_time)+"\n"
        message_for_request+="Please visit your account for further information"  
                                  
        self.send_to(self.usernotifier_port, ('newmsg', ride.offer.request.user.id, message_for_request))
        self.send_to(self.usernotifier_port, ('newmsg', ride.offer.proposal.user.id, message_for_proposal))
        return 1
        
    def routine(self,src,msg):
        """
        The msg treatement routine.
        The only acceptable messages are ('cancelride',rideID,successCancelRide,failureCancelRide)
                                         ('newacceptedride',offerID)
        
        for 'cancelride', see self.cancel_ride(rideID) if the request is valid 
                (ride existing, pending,...) in which case successCancelRide is called
                otherwise failureCancelRide is called with an optional explanation message
        )
        for 'newacceptedride', see self.buildinstruction msg
        """

        if msg[0]=='cancelride':
            if self.cancel_ride(msg[1]):
                threading.Thread(target=msg[2]).start()
            else:
                threading.Thread(target=msg[3]).start()
            
        elif msg[0] == 'newacceptedride':
            res=self.buildinstructions(msg)
        
        else:
            print "unknown message "+msg[0]
        

#timer description
class delayAction:
    def __init__(self, delay, fun, arg):
        self.delay = delay
        self.fun = fun
        self.arg = arg
    def start(self):
        self.t = threading.Timer(self.delay,self.fun,self.arg)
        self.t.start()
    def cancel(self):
        self.t.cancel()
        self.t.join()
    def restart(self):
        self.cancel()
        self.t = threading.Timer(self.delay,self.fun,self.arg)
        self.t.start()
