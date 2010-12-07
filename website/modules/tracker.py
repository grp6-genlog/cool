# @Author Group 6
# Interface of the Tracker

from portobject import *

class Tracker(PortObject):
    rides_list=None # the list of all rides currently observed. A ride is a set(instruction,manual_mode,callb_ok,callb_ko
               #                                                           tcp_connection_driver,tcp_connection_ndriver).
    usernotifier_port=None # the port of the UserNotifier module
    lock=None # the lock of internal datastructures

    def __init__(self,usernotifier_port):
        """
        Initialize self structures.
        @pre : usernotifier_port is the port of the UserNotifier module
        @post : rides_list=list() initialized as an empty list
                self.usernotifier_port=usernotifier_port
                lock is a released lock
                the port_object init has been called called
        """
        self.usernotifier_port = usernotifier_port
        PortObject.__init__(self)

    def check_all_rides(self):
        """
        For all manual rides in the list : 
          @pre : the non-driver has sent a 'ridestart' message.
          @post : the callb_ok procedure is called.
                  the ride is removed from the list.
                  during the remove, the lock has been raised
        or
          @pre : the ridetime is ellapsed since a while.
          @post : the callb_ko procedure is called.
                  the ride is removed from the list.
                  during the remove, the lock has been raised

        For all other rides :
          @pre : the non-driver has sent the 'getdist' message.
          @post : get coordinates from driver tcp and send distance to non_driver tcp
        or
          @pre : the non-driver has sent 'ridestart' message.
          @post : the callb_ok procedure is called.
                  the ride is removed from the list.
                  during the remove, the lock has been raised
        or 
          @pre : the ridetime is ellapsed since a while.
          @post : the callb_ko procedure is called.
                  the ride is removed from the list.  
                  during the remove, the lock has been raised
        """
        pass

    def start_ride(self,instructionID,callb_ok,callb_ko):
        """
        add the ride related to instructionID in the list.
        
        @pre : rides_list is initialized
               DB is initialized
               
               instructionID is a id in the instructions table in the DB
               callb_ok is a procedure
               callb_ko is a procedure
        
        @post : (instruction,manual_mode,callb_ok,callb_ko,tcp_connection_driver,tcp_connection_ndriver) has been
                added to the rides_list.
                      instruction=instructionID
                      callb_ok=//
                      callb_ko=//
                      tcp_connection_* is a tcp connection between * and tracker
                a message is sent to the driver by UserNotifier :
                      ('newmsg',"Don't forget your ride : instructionID")
                a thread is launched with the following 30 min dellayed message through the tcp connection 'ridestarted?'
                during the add, the lock has been raised
        """
        pass

    def routine(self,msg):
        """
        There is two messages received by tracker : 
        ('startride',instruID)
        @pre : instruId is the id of an instruction in DB
        @post : start_ride is called.
        ('check')
        @pre : True
        @post : check_all_rides is called
                a 5s dellayed message is set to the module port ('check')
                
        """
        pass
    
    
