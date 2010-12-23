#@Author Group 6

from portobject import *
from website.offers.models import Offer
from website.rides.models import Ride
from website.proposals.models import Proposal
from website.requests.models import Request
from website.profiles.models import UserProfile
import threading

class PaymentManager(PortObject):
    def __init__(self):
        """
        @pre : the payment manager has not already been initialized
        @post : the payment manager is initialized
        """
        PortObject.__init__(self)
        
    def fee_transfer(self,instructionID):
        """Transfer the fee from account of userID1 to the account of userID2
        @pre : DB is initialized
               userID1 is the id of the user where the fee is withdrawn
               userID2 is the id of the user where the fee is added
               fee is the amount of fee in float
        @post : the account of userID1 contains fee money less and the account of userID2 contains fee 
                money more
        """
        ride = Ride.objects.get(id=instructionID)
        fee=ride.offer.total_fee
        driver=ride.offer.proposal.user
        ndriver=ride.offer.request.user        
        ndriver.account_balance=ndriver.account_balance-fee
        driver.account_balance=driver.account_balance+fee
        driver.save()
        ndriver.save()

    def valid_transfer(self,bankAccount,communication,amount):
        """
        In user we trust.
        @pre : \
        @post : return if the transfer is valid
        """
        return True

    def transfer_money(self,bankAccount,communication,amount):
        """
        In us we trust.
        @pre : \
        @post : transfer the money to the bank account
        """
        print 'Transfer sent to bank:',bankAccount,communication,amount
        return True

    def add_money(self,userID, bankAccount, communication, amount):
        """Add money from bank account to car pooling system account
        @pre : userID is the id of the user who wants to add the money
               bankAccount is the bank account where the money comes from
               communication is the communication of the transfer to recognize the payment
               DB is initialized
               amount is the amount of money to transfer
        @post : the account of userID is incremented by the money amount coming from the bank transfer
        """
        if not self.valid_transfer(bankAccount,communication,amount):
            return False 
        else:
            user1=UserProfile.objects.get(id=userID)
            user1.account_balance+=amount
            user1.save()
            return True
        
    def get_money(self,userID, bankAccount, amount):
        """Withdraw the money amount from account to bank account
        @pre : userID is the id of the user who wants to get the money
               bankAccount is the bank account where the money should go
               DB is initialized
               amount is a float representing the amount of money to transfer
        @post : the account of userID contains is decremented by the amount of money specified
                and this amount of money is transferred to bankAccount
        """
        user=UserProfile.objects.get(id=userID)
        if(user.account_balance-amount<0):
            return False
        else:
            user.account_balance-=amount
            if not self.transfer_money(bankAccount,str(userID),amount):
                return False
            user.save()
            return True
        
    def routine(self, src, msg):
        """This is the message routine handler
        The messages accepted are the pairs ('payfee', instructionID), ('addmoney', [userID, srcBankAccount, communication, amount], callbackOk,callbackKo), ('getmoney', [userID, dstBankAccount, amount], callbackOk,callbackKo)
        
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
        if len(msg)==2:
            (name,instructionID)=msg
            self.fee_transfer(instructionID)
            
        if len(msg)==4:
            (name,tab,functionOk,functionKo) = msg
            if name=='addmoney':
                if(self.add_money(tab[0],tab[1],tab[2],tab[3])):
                    threading.Thread(target=functionOk).start()
                else:
                    threading.Thread(target=functionKo).start()
            elif name=='getmoney':
                if self.get_money(tab[0],tab[1],tab[2]):
                    threading.Thread(target=functionOk).start()
                else:
                    threading.Thread(target=functionKo).start()
