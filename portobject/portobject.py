#! /usr/bin/env python
# Author Group 6
# A port object

from threading import Thread
from Queue import Queue

def anonymous_send_to(dest,msg):
    dest.put((None,msg))

class PortObject(Thread):
    port = None # the port of the object (a queue)

    def __init__(self):
        """
        Build the port as an empty queue and initialize the thread. 
        """
        self.port = Queue() # Initialize an infinite empty queue
        Thread.__init__(self) # Initialze the thread
        self.start() # Launch the thread
        

    def run(self):
        """
        The main routine of the PortObject. Wait until it has a message in its port then treat it.
        """
        while True:
            src,message = self.port.get(block=True)
            if message == "quit":
                break
            self.routine(src,message)

    def send_to(self,dest,msg):
        """
        Send a message to the specified dest port. 
        @pre : dest is a port from a PortObject.
        @post : the pair (self.port,msg) has been sent to dest (add in dest since its a queue).
                neither dest neither msg have been modified.  
        """
        dest.put((self.port,msg))
    
    def routine(self,src,msg):
        """
        Treat a msg.
        """
        abstract


    def get_port(self):
        """
        Returns the port of the PortObject.
        """
        return self.port
