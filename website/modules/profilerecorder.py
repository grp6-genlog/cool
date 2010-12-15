# @Author Group 6
# Interface of the RequestRecorder module

from portobject import *
from profiles.models import *
import threading
import traceback

USERID = 0
NBSEATS = 1
BIRTHDATE = 2
SMOKER = 3
COMMUNITIES = 4
MONEYPERKM = 5
GENDER = 6
BANKACCOUNT = 7
CARID = 8
GSMNUMBER = 9
CARDESCRIPTION = 10
SMARTPHONE = 11

class ProfileRecorder(PortObject):
    
    def __init__(self):
        """
        Initialize self.DB
        @pre DBG is the SQL database
        @post self.DB = DBG
        """
        PortObject.__init__(self)
    
    def routine(self,src,msg):
        """
        The msg treatement routine.
        The only acceptable messages are the pairs ('recordprofile',[UserID,NumberOfSeats,
                                                                    BirthDate,Smoker,Communities,MoneyPerKm,
                                                                    Gender,BankAccountNumber,CarID,
                                                                    GSMNumber,CarDescription,SmartphoneID],
                                                                    SuccessCallBack,FailureCallBack,request)
                                                   ('updateprofile',[UserID,UserPassword,NumberOfSeats,
                                                                    BirthDate,Smoker,Communities,MoneyPerKm,
                                                                    Gender,BankAccountNumber,CarID,
                                                                    GSMNumber,CarDescription,SmartphoneID],
                                                                    SuccessCallBack,FailureCallBack,request)
        @pre : DB is initialized and is the SQL database
               
               UserID is an integer
               NumberOfSeats is an integer
               BirthDate is a (datetime.date)
               Smoker is a boolean
               Communities is a string
               MoneyPerKm is a float
               Gender is a string
               BankAccountNumber is a string
               CarID is a string
               GSMNumber is a string
               CarDescription is a string
               SmartphoneID is string
               SuccessCallBack is a procedure 
               FailureCallBack is a procedure
      
        @post : If the first element of the pair in the message was 'recordprofile'
                the specified profile is added to the DB (in the profile table).
                If the first element of the pair in the message was 'updateprofile'
                the profile corresponding to the UserId specified updates every field
                of this profile in the database for which the corresponding element
                in the list was not None.
                If no error or unexpected events happened, the SuccessCallBack procedure
                has been executed, otherwise FailureCallBack has been executed.
        """
        if msg[0] == 'recordprofile':
            try:
                lfields = msg[1]
                pro = UserProfile()
                
                pro.user = lfields[USERID]
                pro.number_of_seats = lfields[NBSEATS]
                pro.date_of_birth = lfields[BIRTHDATE]
                pro.smoker = lfields[SMOKER]
                pro.communities = lfields[COMMUNITIES]
                pro.money_per_km = lfields[MONEYPERKM]
                pro.gender = lfields[GENDER]
                pro.bank_account_number = lfields[BANKACCOUNT]
                pro.car_id = lfields[CARID]
                pro.phone_number = lfields[GSMNUMBER]
                pro.car_description = lfields[CARDESCRIPTION]
                pro.smartphone_id = lfields[SMARTPHONE]
                
                pro.save()
            except:
                traceback.print_exc()
                #threading.Thread(target = msg[3], args = (msg[4],)).start()
                msg[3](msg[4])
            else:
                #threading.Thread(target = msg[2], args = (msg[4],)).start()
                msg[2](msg[4])
        elif msg[0] == 'updateprofile':
            try:
                lfields = msg[1]
                pro = UserProfile.objects.get(user=lfields[USERID])

                if lfields[NBSEATS]:
                    pro.number_of_seats = lfields[NBSEATS]
                if lfields[BIRTHDATE]:
                    pro.date_of_birth = lfields[BIRTHDATE]
                if lfields[SMOKER]:
                    pro.smoker = lfields[SMOKER]
                if lfields[COMMUNITIES]:
                    pro.communities = lfields[COMMUNITIES]
                if lfields[MONEYPERKM]:
                    pro.money_per_km = lfields[MONEYPERKM]
                if lfields[GENDER]:
                    pro.gender = lfields[GENDER]
                if lfields[BANKACCOUNT]:
                    pro.bank_account_number = lfields[BANKACCOUNT]
                if lfields[CARID]:
                    pro.car_id = lfields[CARID]
                if lfields[GSMNUMBER]:
                    pro.phone_number = lfields[GSMNUMBER]
                if lfields[CARDESCRIPTION]:
                    pro.car_description = lfields[CARDESCRIPTION]
                if lfields[SMARTPHONE]:
                    pro.smartphone_id = lfields[SMARTPHONE]
                
                pro.save()
            except:
                threading.Thread(target = msg[3], args = (msg[4],)).start()
            else:
                threading.Thread(target = msg[2], args = (msg[4],)).start()
        else:
            print 'ProfileRecorder received an unexpected message'
