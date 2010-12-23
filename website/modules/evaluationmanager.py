#@Author Group 6
#Interface of the Evaluation Manager Module

from portobject import *
from evaluations.models import Evaluation
from rides.models import Ride
from offers.models import Offer
from profiles.models import UserProfile
from django.contrib.auth.models import User
import threading, datetime

"""
Evaluation manager agent implementation
"""
class EvaluationManager(PortObject):
	
	def __init__(self):
		"""Initialize DB
		@pre : \
		@post : the portobject of the evaluation manager is initiated
		"""
		PortObject.__init__(self)
		
	def updateEvaluation(self,rideID, userID, content):
		"""Make an evaluation for a user with id userID and related with the instructionID
		@pre : rideID is the id of the ride
			   userID is the id of the user
			   content is the content of the evaluation, a pair (note, comment)
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
		@pre : evaluationID is in database
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
			   rideID is the id of the ride
		@post : the empty evaluation for userID and instructionID is now present in DB
		        the thread that will launch the delay making the evaluation 
		        after 3 days unavailable is launched.
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

"""
This is the timer that we use to delay the actions
"""
class delayAction:
    """
        @pre : \
        @post : the timer delayAction is initiated
    """
	def __init__(self, delay, fun, arg):
		self.delay = delay
		self.fun = fun
		self.arg = arg
	
	"""
	    @pre : the timer has been initiated
	    @post : a thread that will launch the functio
	    
	    n self.fun with
	    arguments self.arg after a delay self.delay is launched. 
	"""
	def start(self):
		self.t = threading.Timer(self.delay,self.fun,self.arg)
		self.t.start()
        
    """
        @pre : the delayAction instance has already been started
        @post : the thread launched in start is stopped
    """        
	def cancel(self):
		self.t.cancel()
		self.t.join()
	
	"""
	    @pre : the delayAction instance has already been started
	    @post : the thread launched in start is restarted
	"""
	def restart(self):
		self.cancel()
		self.t = Timer(self.delay,self.fun,self.arg)
		self.t.start()
			 
	
