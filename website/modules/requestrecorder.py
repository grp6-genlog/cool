# @Author Group 6
# Interface of the RequestRecorder module

from portobject import *
from requests.models import *

import threading, traceback

USERID = 0
DEPPOINT = 1
DEPRANGE = 2
ARRPOINT = 3
ARRRANGE = 4
ARRTIME = 5
MAXDELAY = 6
NBSEATS = 7
CANCMARG = 8

class RequestRecorder(PortObject):
    findpair_port = None # the communication port of FindPair

    def __init__(self,findpair_portG):
        """
        Initialize self, DB, findpair_port.
        @pre findpair_portG is the FindPair module port (a Queue)
        @post self.findpair_port = findpair_portG              
        """
        self.findpair_port = findpair_portG
        PortObject.__init__(self)
    
    def routine(self,src,msg):
        """
        The msg treatement routine.
        The only acceptable message is the pair ('recordrequest',[UserID,departurePoint,departureRange,
                                                                  arrivalPoint,arrivalRange,arrivalTime,maxDelay,
                                                                  nbRequestedSeats,cancellationMargin],
                                                                  SuccessCallBack,FailureCallBack,user)
        @pre : DB is initialized and is the SQL database
               findpair_port is the FindPair module's port

               UserID is a string
               departurePoint is a pair of float
               departureRange is a float
               arrivalPoint is a pair of float
               arrivalRange is a float
               arrivalTime is a (datetime.date,datetime.time)
               maxDelay is a datetime.time
               nbRequestedSeats is an integer
               cancellationMargin is a datetime.time
               SuccessCallBack is a procedure
               FailureCallBack is a procedure
      
        @post : The specified request is added to the DB (in the request table).
                a msg is sent to FindPair module via findpair_port with the following message : 
                  ('newrequest',rID) with rID the id of the request in the DB's table.
                If no error or unexpected events happened, the SuccessCallBack procedure
                has been executed, otherwise FailureCallBack has been executed.
        """
        if msg[0] == 'recordrequest':
            
            try:
                lfields = msg[1]
                req = Request()
                print lfields
                req.user = lfields[USERID]
                req.departure_point_lat = lfields[DEPPOINT][0]
                req.departure_point_long = lfields[DEPPOINT][1]
                req.departure_range = lfields[DEPRANGE]
                req.arrival_point_lat = lfields[ARRPOINT][0]
                req.arrival_point_long = lfields[ARRPOINT][1]
                req.arrival_range = lfields[ARRRANGE]
                req.arrival_time = lfields[ARRTIME]
                req.max_delay = lfields[MAXDELAY]
                req.nb_requested_seats = lfields[NBSEATS]
                req.cancellation_margin = lfields[CANCMARG]

                req.save()
                req_id = req.id
            except:
                traceback.print_exc()
                threading.Thread(target = msg[3], args = (msg[4],)).start()
            else:  
                self.send_to(self.findpair_port, ('newRequest', req_id))
                threading.Thread(target = msg[2], args = (msg[4],)).start()
        else:
            print 'RequestRecorder received an unexpected message'
