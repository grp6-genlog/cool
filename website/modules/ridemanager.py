# @Author Group 6
# Interface of the RequestRecorder module

from portobject import *

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
                  ('newmsg',nondriverID,"You've got a ride for request requestID. Please visit your account for further information.")
                  ('newmsg',driverID,"You've got a shared ride for proposalID. Please visit your account for further information.")
                a thread is run to send the following differed message to Tracker at rideTime - 30min:
                  ('startride',instructionID,closeRide(),cancelRide()) with instructionID the id of the request in the DB's table. and closeRide,cancelRide callback functions = lambda close_ride(self,instructionID).
                a thread is run to send the following differed message to RideManager at rideTime:
                  ('startevaluation',instructionID) with instructionID the id of the request in the DB's table.
        """
        pass

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
        pass

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
        pass

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
        pass
