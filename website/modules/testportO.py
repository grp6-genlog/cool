#! /usr/bin/env python
# Author Group 6
# A port object

from portobject import *

class SrcPortObject(PortObject):
    counter = 0 
    ID = 0

    def __init__(self, ID):
        self.counter = 0
        self.ID = ID
        PortObject.__init__(self)

    def routine(self,src,message):
        if message == 'ack':
            self.counter +=1
        if self.counter == 10000:
            print 'Transmitted ok', self.ID

    def barbare_send(self,dest):
        for x in xrange (10000):
            self.send_to(dest,'test')
        print '10000 sent'

class DestPortObject(PortObject):
    
    def routine(self,src,message):
        if message == 'test':
            self.send_to(src,'ack')

dest = DestPortObject()
for i in xrange(100):
    src = SrcPortObject(i+1)
    src.barbare_send(dest.get_port())


