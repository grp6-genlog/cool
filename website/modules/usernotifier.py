# @Author Group 6
# Interface of the UserNotifier module

from portobject import *
import smtplib
import traceback

from website.profiles.models import UserProfile

class UserNotifier(PortObject):
    fromaddr = 'carpooling.cool@gmail.com'
    server = None

    def __init__(self):
        """
    Initialize the module
    @pre db is the SQL database of our system
    @post self.dbconn=db
          initialize the port object
        """
        PortObject.__init__(self)
        self.server = smtplib.SMTP('smtp.gmail.com:587')  
        self.server.starttls()  
        self.server.login('carpooling.cool','genlogiscool')  

    def SendMessageToUser(self,userID=None,message=None):
        """
        Sends a notification to user thru a desired medium
        @pre:    dbconn is the SQL database
            userID is the user to send the notification
            message is the message to send
        
        @post:    The message has been sent to user using his desired device
        """
        u = UserProfile.objects.get(id=userID)
        mail = u.user.email
        tries = 50
        print "sending email to "+mail
        while tries>0:
            try:
                self.server.sendmail(self.fromaddr, mail, message)  
                break
            except:
                self.server = smtplib.SMTP('smtp.gmail.com:587')  
                self.server.starttls()  
                self.server.login('carpooling.cool','genlogiscool')  
            tries-=1

    def routine(self,src,msg):
        """
        The only acceptable msg is ( newmsg ,userID,strmessage)
        @pre : dbconn is initialized
        userID is the id of a user in the dbconn
        strmessage is a string
        @post : the send_message_to_user is called.
        """

        if msg[0]=='newmsg':
            userID=msg[1]
            message=msg[2]
            self.SendMessageToUser(userID,message)
        else:
            print "message unknown : "+str(msg[0])
