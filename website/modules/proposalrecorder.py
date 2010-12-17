# @Author Group 6
# Interface of the RequestRecorder module

from portobject import *
from proposals.models import *
import threading, traceback

USERID = 0
ROUTEPOINTS =1
CARDESCRIPTION = 2
CARID = 3
NBSEATS = 4
MONEYPERKM = 5
DEPTIME = 6
ARRTIME = 7

class ProposalRecorder(PortObject):
    findpair_port=None # the communication port of FindPair
    
    def __init__(self,findpair_portG):
        """
        Initialize  findpair_port.
        @pre findpair_portG is the FindPair module port (a Queue)
        @post self.findpair_port = findpair_portG
        """
        self.findpair_port = findpair_portG
        PortObject.__init__(self)
    
    def routine(self,src,msg):
        """
        The msg treatement routine.
        The only acceptable message is the pair ('recordproposal',[UserID,RoutePoints,CarDescription,
                                                                  CarID,NumberOfSeats,MoneyPerKm,DepartureTime,ArrivalTime],
                                                                  SuccessCallBack,FailureCallBack)
        @pre : DB is initialized and is the SQL database
               findpair_port is the FindPair module's port
               
               UserID is a string
               RoutePoints is a list of minimal length 2 containing pairs of floats
               CarDescription is a string
               CarID is a string
               NumberOfSeats is a integer
               MoneyPerKm is a float
               DepartureTime is a datetime.date
               SuccessCallBack is a procedure 
               FailureCallBack is a procedure
      
        @post : The specified proposal is added to the DB (in the proposal table).
                a msg is sent to FindPair module via findpair_port with the following message : 
                ('newproposal',pID) with pID the ID of the proposal in the DB's table.
                If no error or unexpected events happened, the SuccessCallBack procedure
                has been executed, otherwise FailureCallBack has been executed.
        """
        if msg[0] == 'recordproposal':
            try:
                lfields = msg[1]
                prop = Proposal()

                prop.user = lfields[USERID]
                prop.car_id = lfields[CARID]
                prop.car_description = lfields[CARDESCRIPTION]
                prop.number_of_seats = lfields[NBSEATS]
                prop.money_per_km = lfields[MONEYPERKM]
                prop.departure_time = lfields[DEPTIME]
                prop.arrival_time = lfields[ARRTIME]
                
                prop.save()
                prop_id = prop.id
                
                order = 0
                for routePoint in lfields[ROUTEPOINTS]:
                    rp = RoutePoints()
                    rp.proposal = prop
                    rp.latitude = routePoint[0]
                    rp.longitude = routePoint[1]
                    rp.order = order
                    rp.save()
                    
                    order += 1

            except:
                traceback.print_exc()
                threading.Thread(target = msg[3], args = (msg[4],)).start()
            else:  
                self.send_to(self.findpair_port, ('newproposal', prop_id))
                threading.Thread(target = msg[2], args = (msg[4],)).start()
        else:
            print 'ProposalRecorder received an unexpected message'
