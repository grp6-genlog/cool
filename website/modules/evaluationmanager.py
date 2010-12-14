#@Author Group 6
#Interface of the Evaluation Manager Module

from portobject import *
from evaluations.models import Evaluation
from rides.models import Ride
from offers.models import Offer

class EvaluationManager(PortObject):
	
	def __init__(self):
		"""Initialize DB
		@pre : DB is the database written in SQL
		@post : self.DB=DB
		"""
		PortObject.__init__(self)
		
	def updateEvaluation(instructionID, userID, content):
		"""Make an evaluation for a user with id userID and related with the instructionID
		@pre : instructionID is the id of the instruction
			   userID is the id of the user
			   content is the content of the evaluation, a pair (note, comment)
			   DB is a database that is initialized and the evaluation related to instructionID and
			   userID is already in database, but empty
		@post : the evaluation contains now the content
		"""
		evals=Evaluation.objects.filter(id=evaluationID)
		if len(evals)!=1:
			raise "There isn't any valid offer for this ID"
		if not evals[0].locked:
			evals[0].rating=content[0]
			evals[0].content=content[1]
			return 0
		return -1
		
	def lockEvaluation(evaluationID):
		"""Lock the evaluation and evaluate is not more possible for this evaluation
		@pre : DB is initialized and evaluationID is in database
			 evaluationID is the id of the evaluation
		@post : the evaluation is now locked
		"""
		evals=Evaluation.objects.filter(id=evaluationID)
		if len(evals)==0:
			raise "There doesn't exist an offer"
		evals.locked=True
		
	def buildEmptyEvaluation(userID, instructionID):
		"""Make an empty evaluation for userID and instructionID
		@pre : userID is the id of a user
			   instructionID is the id of an instruction
			   DB in initialized
		@post : the empty evaluation for userID and instructionID is now present in DB
		"""
		rides=Ride.objects.filter(offer=instructionID)
		if len(rides)==0:
			raise "The ride doesn't exist for this offer"
		proposals=Proposal.objects.filter(id=rides[0].proposal)
		requests=Request.objects.filter(id=rides[0].request)
		if len(proposals)==0 or len(requests)==0:
			raise "The requests or the proposals doesn't exist from this offer"
		if proposals[0].user!=userID:
			u_from=proposals[0].user
		eval=Evaluation(ride=rides[0], user_from=u_from, user_to=userID, locked=False)
		eval.save()
		
	def routine(self, src, msg):
		"""The message routine handler
		The messages accepted are the pairs ('startevaluation', [userId,instructionid]),
		('evaluate', [instructionid, userId, content],callback) and ('closeevaluation', [evaluationid])
		
		@pre : DB is initialized and is a SQL Database
			 instructionid is an id for the instruction (int)
			 userId is an id for the user involved in instruction (int)
			 evaluationid is an if for the evaluation (int)
			content is the content of an evaluation, composed of a pair (note, comment)
			 
		@post : - if the message received is 'startevaluation', a empty evaluation for instruction 
			  are created in the database and a delayed timer is started form closeevaluation 				 
			   - if the message received is 'evaluate', the evaluation concerning instruction and userID is updated with the content. A call back function is called
			  	- if the message received is 'closeevaluation', the timer has sent message to lock the evaluation.
			  no evaluation is now possible
		"""
		if msg[0]=='startevaluation':
			buildEmptyEvaluation(msg[1][0], msg[1][1])
		elif msg[0]=='evaluate':
			res=updateEvaluation(msg[1][0], msg[1][1], msg[1][2])
			callback(res)
		elif msg[0]=='closeevaluation':
			lockEvaluation(msg[1][0])
			 
	
