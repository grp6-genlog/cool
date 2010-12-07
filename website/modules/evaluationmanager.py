#@Author Group 6
#Interface of the Evaluation Manager Module

from portobject import *

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
		pass
		
	def lockEvaluation(evaluationID):
		"""Lock the evaluation and evaluate is not more possible for this evaluation
		@pre : DB is initialized and evaluationID is in database
			 evaluationID is the id of the evaluation
		@post : the evaluation is now locked
		"""
		
	def buildEmptyEvaluation(userID, instructionID):
		"""Make an empty evaluation for userID and instructionID
		@pre : userID is the id of a user
			   instructionID is the id of an instruction
			   DB in initialized
		@post : the empty evaluation for userID and instructionID is now present in DB
		"""
		
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
		pass
			 
	
