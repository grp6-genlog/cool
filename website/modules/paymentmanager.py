#@Author Group 6
#Interface of the Payment Manager Module

from portobject import *

class PaymentManager(PortObject):

	
	def __init__(self):
		"""Initialize self.DB
		@pre : DB is a database written in SQL
		@post : self.DB=DB
		"""
		PortObject.__init__(self)
		
	def fee_transfer(userID1, userID2, fee):
		"""Transfer the fee from account of userID1 to the account of userID2
		@pre : DB is initialized
			   userID1 is the id of the user where the fee is withdrawn
			   userID2 is the id of the user where the fee is added
			   fee is the amount of fee in float
		@post : the account of userID1 contains fee money less and the account of userID2 contains fee 
				money more
		"""
		pass
		
	def add_money(userID, bankAccount, communication, amount):
		"""Add money from bank account to car pooling system account
		@pre : userID is the id of the user who wants to add the money
			   bankAccount is the bank account where the money comes from
			   communication is the communication of the transfer to recognize the payment
			   DB is initialized
			   amount is the amount of money to transfer
		@post : the account of userID is incremented by the money amount coming from the bank transfer
		"""
		pass
		
	def get_money(userID, bankAccount, amount):
		"""Withdraw the money amount from account to bank account
		@pre : userID is the id of the user who wants to get the money
		       bankAccount is the bank account where the money should go
		       DB is initialized
		       amount is a float representing the amount of money to transfer
		@post : the account of userID contains is decremented by the amount of money specified
		        and this amount of money is transferred to bankAccount
		"""
		pass
		
	def routine(self, src, msg):
		"""This is the message routine handler
		The messages accepted are the pairs ('payfee', [userID1, userID2, fee]), ('addmoney', [userID, srcBankAccount, communication], callback), ('getmoney', [userID, dstBankAccount, amount], callback)
		
		@pre : DB is initialized as a SQL Database
			userID is the id of a user (int)
			fee is the fee to pay (float)
			src(dst)BankAccount is a bank account number (string)
			 
		@post : - if the message received is 'payfee', the amount of fee is 
			withdrawn to the userID1 account and added to userID2 account
		      - if the message received is 'addmoney' the amount from a money transfer. The call
			back function is called
			described in communication and srcBankAccount is added to the account of userID
		      - if the message received is 'getmoney' the amount of money of the userID's account is 
			removed and sent to the dstBankAccount. The call back function is called.
		"""
		pass
		
