#@Author Group 6
#Interface of the Evaluation Manager Module

from portobject import *
from evaluations.models import Evaluation
from rides.models import Ride
from offers.models import Offer
from profiles.models import UserProfile
from django.contrib.auth.models import User
import threading, datetime

class EvaluationManager(PortObject):
	
	def __init__(self):
		"""Initialize DB
		@pre : DB is the database written in SQL
		@post : self.DB=DB
		"""
		PortObject.__init__(self)
		
	def updateEvaluation(self,rideID, userID, content):
		"""Make an evaluation for a user with id userID and related with the instructionID
		@pre : instructionID is the id of the instruction
			   userID is the id of the user
			   content is the content of the evaluation, a pair (note, comment)
			   DB is a database that is initialized and the evaluation related to instructionID and
			   userID is already in database, but empty
		@post : the evaluation contains now the content
		"""
        
		evaluation = Evaluation.objects.get(ride = Ride.objects.get(id = rideID), user_from=UserProfile.objects.get(id=userID))
		if not evaluation.locked:
			evaluation.rating = content[0]
			evaluation.content = content[1]
			evaluation.save()
			return 1
		return 0
		
	def lockEvaluation(self,evaluationID):
		"""Lock the evaluation and evaluate is not more possible for this evaluation
		@pre : DB is initialized and evaluationID is in database
			 evaluationID is the id of the evaluation
		@post : the evaluation is now locked
		"""
		evals = Evaluation.objects.filter(id=evaluationID)
		if len(evals) == 0:
			raise "There isn't any valid offer for this ID"
		evals.locked = True
		
	def buildEmptyEvaluation(self,userID, rideID):
		"""Make an empty evaluation for userID and instructionID
		@pre : userID is the id of a user
			   instructionID is the id of an instruction
			   DB in initialized
		@post : the empty evaluation for userID and instructionID is now present in DB
		"""
		ride = Ride.objects.get(id = rideID)
		if ride.offer.proposal.user.id!=userID:
			u_from = ride.offer.proposal.user
		else:
			u_from = ride.offer.request.user
		myeval = Evaluation(ride=ride, user_from=u_from, user_to=UserProfile.objects.get(id=userID), locked=False, ride_time=datetime.datetime.today())
		myeval.save()
		delay = delayAction(86400*3, self.send_to, (self.get_port, ('closeevaluation', myeval.id)))
		delay.start()
		
	def routine(self, src, msg):
		"""The message routine handler
		The messages accepted are the pairs ('startevaluation', userId,instructionid),
		('evaluate', instructionid, userId, content,callback) and ('closeevaluation', evaluationid)
		
		@pre :	 rideid is an id for the ride (int)
			 userId is an id for the user involved in instruction (int)
			 evaluationid is an if for the evaluation (int)
			content is the content of an evaluation, composed of a pair (note, comment)
			 
		@post : - if the message received is 'startevaluation', a empty evaluation for instruction 
			  are created in the database and a delayed timer is started form closeevaluation 				 
			   - if the message received is 'evaluate', the evaluation concerning instruction and userID is updated with the content. A call back function is called
			  	- if the message received is 'closeevaluation', the timer has sent message to lock the evaluation.
			  no evaluation is now possible
		"""
		if msg[0] == 'startevaluation':
			self.buildEmptyEvaluation(msg[1], msg[2])
		elif msg[0] == 'evaluate':
			if self.updateEvaluation(msg[1], msg[2], msg[3]):
			    threading.Thread(target=msg[4]).start()
			else:
			    threading.Thread(target=msg[5]).start()

		elif msg[0] == 'closeevaluation':
			self.lockEvaluation(msg[1])

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
		self.t = Timer(self.delay,self.fun,self.arg)
		self.t.start()
			 
	
