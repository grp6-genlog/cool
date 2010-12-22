# @Author Group 6
# Interface of the RequestRecorder module

from portobject import *
from profiles.models import *
import threading, traceback

USERID = 0
USERNAME = 0
PASSWORD = 1
EMAIL = 2
FIRST = 3
LAST = 4

NBSEATS = 5
BIRTHDATE = 6
SMOKER = 7
COMMUNITIES = 8
MONEYPERKM = 9
GENDER = 10
BANKACCOUNT = 11
CARID = 12
GSMNUMBER = 13
CARDESCRIPTION = 14

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
        The only acceptable messages are the pairs ('recordprofile',[username, pwd, email,
                                                                    first_name, last_name, NumberOfSeats,
                                                                    BirthDate, Smoker, Communities,
                                                                    MoneyPerKm, Gender, BankAccountNumber,
                                                                    CarID, GSMNumber, CarDescription],
                                                    callback_ok, callback_ok)
                                                   ('updateprofile',[userid, None, email,
                                                                    first_name, last_name, NumberOfSeats,
                                                                    BirthDate, Smoker, Communities,
                                                                    MoneyPerKm, Gender, BankAccountNumber,
                                                                    CarID, GSMNumber, CarDescription],
                                                    callback_ok, callback_ok)
                                                   ('changepass',[userid, newpass],
                                                    callback_ok, callback_ok)
                                                    
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
                
                
                usr = User.objects.create_user(lfields[USERNAME], lfields[EMAIL], lfields[PASSWORD])
                usr.first_name = lfields[FIRST]
                usr.last_name = lfields[LAST]
                usr.save()
                
                pro = UserProfile()
                pro.user = usr
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
                
                pro.save()
            except:
                traceback.print_exc()
                threading.Thread(target = msg[3],).start()
            else:
                threading.Thread(target = msg[2],).start()
                
        elif msg[0] == 'updateprofile':
            try:
                lfields = msg[1]
                
                usr = User.objects.get(id=lfields[USERID])
                if lfields[EMAIL] != None:
                    usr.email = lfields[EMAIL]
                if lfields[FIRST] != None:
                    usr.first_name = lfields[FIRST]
                if lfields[LAST] != None:
                    usr.last_name = lfields[LAST]
                
                usr.save()
                pro = UserProfile.objects.get(user=usr)

                if lfields[NBSEATS] != None:
                    pro.number_of_seats = lfields[NBSEATS]
                
                if lfields[BIRTHDATE] != None:
                    pro.date_of_birth = lfields[BIRTHDATE]
                
                pro.smoker = lfields[SMOKER]
                
                if lfields[COMMUNITIES] != None:
                    pro.communities = lfields[COMMUNITIES]
                if lfields[MONEYPERKM] != None:
                    pro.money_per_km = lfields[MONEYPERKM]
                if lfields[GENDER] != None:
                    pro.gender = lfields[GENDER]
                if lfields[BANKACCOUNT] != None:
                    pro.bank_account_number = lfields[BANKACCOUNT]
                if lfields[CARID] != None:
                    pro.car_id = lfields[CARID]
                if lfields[GSMNUMBER] != None:
                    pro.phone_number = lfields[GSMNUMBER]
                if lfields[CARDESCRIPTION] != None:
                    pro.car_description = lfields[CARDESCRIPTION]
                
                pro.save()
            except:
                traceback.print_exc()
                threading.Thread(target = msg[3],).start()
            else:
                threading.Thread(target = msg[2],).start()
        elif msg[0] == 'changepass':
            try:
                lfields = msg[1]
                
                usr = User.objects.get(id=lfields[USERID])
                usr.set_password(lfields[PASSWORD])
                usr.save()
                
            except:
                traceback.print_exc()
                threading.Thread(target = msg[3],).start()
            else:
                threading.Thread(target = msg[2],).start()
        else:
            print 'ProfileRecorder received an unexpected message'
