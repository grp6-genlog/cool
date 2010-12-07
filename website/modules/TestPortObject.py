#!/usr/bin/python

import unittest
from thread import *
from portobject import *

class PortObjectTester(PortObject):
	
	def __init__(self):
		self.check=False
		self.count=0
		PortObject.__init__(self)

	def routine(self, src, msg):
		m, ack=msg
		if m=='test1':
			self.check=True
			ack.put('ack')
		elif m=='test2':
			self.count+=1
			ack.put('ack')
		elif m[0]=='test3':
			ack.put('ack %d' % m[1])
		else:
			print 'Message missunderstood'
			ack.put('nack')

class Counter(Thread):
	def __init__(self, nb, port, q):
		self.nb=nb
		self.port=port
		self.q=q
		Thread.__init__(self)
		
	def run(self):
		for i in xrange(0,self.nb):
			anonymous_send_to(self.port.get_port(), ('test2', self.q))

class TestPortObject(unittest.TestCase):

	def setUp(self):
		self.port1=PortObjectTester()
		self.q=Queue()
	
	def test_simplecheck(self):
		anonymous_send_to(self.port1.get_port(), ('test1', self.q))
		ack=self.q.get()
		self.assertEqual(ack,'ack')
		self.assertTrue(self.port1.check)

	def test_counter(self):
		for i in xrange(0,100):
			anonymous_send_to(self.port1.get_port(), ('test2', self.q))
		for i in xrange(0,100):
			ack=self.q.get()
			self.assertEqual(ack,'ack')
		self.assertEqual(self.port1.count, 100)

	def test_order(self):
		for i in xrange(0,100):
			anonymous_send_to(self.port1.get_port(), (('test3',i), self.q))
		for i in xrange(0,100):
			ack=self.q.get()
			self.assertEqual(ack,'ack %d' % i)


	def test_multi_counter(self):
		q=Queue()
		c1=Counter(250, self.port1, q)
		c2=Counter(300, self.port1, q)
		c1.start()
		c2.start()
		for i in xrange(0, 550):
			ack=q.get()
			self.assertEqual(ack, 'ack')

		self.assertEqual(self.port1.count, 550)

	def tearDown(self):
		anonymous_send_to(self.port1.get_port(), 'quit')


if __name__=='__main__':
	suite=unittest.TestLoader().loadTestsFromTestCase(TestPortObject)
	unittest.TextTestRunner(verbosity=2).run(suite)

