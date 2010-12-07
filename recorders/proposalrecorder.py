# @Author Group 6
# Interface of the RequestRecorder module

from portobjectIF import *
from proposals.models import *

USERID = 0
ROUTEPOINTS =1
CARDESCRIPTION = 2
CARID = 3
NBSEATS = 4
MONEYPERKM = 5
DEPTIME = 6

class ProposalRecorder(PortObject):
    DB # the database
    findpair_port # the communication port of FindPair
    
    def __init__(self,DBG,findpair_portG):
        """
        Initialize self DB, findpair_port.
        @pre DBG is the SQL database
             findpair_portG is the FindPair module port (a Queue)
        @post self.DB = DBG
              self.findpair_port = findpair_portG
        """
        self.findpair_port = findpair_portG
        PortObject.__init__(self)
    
    def routine(self,src,msg):
        """
        The msg treatement routine.
        The only acceptable message is the pair ('recordproposal',[UserID,RoutePoints,CarDescription,
                                                                  CarID,NumberOfSeats,MoneyPerKm,DepartureTime],
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
                
                prop.save()
                prop_id = prop.id

                for routePoint in lfields[ROUTEPOINTS]:
                    rp = RoutePoint()
                    rp.proposal = prop_id
                    rp.latitude = routePoint[0]
                    rp.longitude = routePoint[1]
                    rp.save()

            except:
                threading.Thread(target = msg[3]).start()
            else:  
                send_to(findpair_port, ('newProposal', req_id))
                threading.Thread(target = msg[2]).start()
        else:
            print 'ProposalRecorder received an unexpected message'
