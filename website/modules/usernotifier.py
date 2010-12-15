# @Author Group 6
# Interface of the UserNotifier module

from portobject import *
import smtplib

class UserNotifier(PortObject):

    def __init__(self):
        """
    Initialize the module
    @pre db is the SQL database of our system
    @post self.dbconn=db
          initialize the port object
        """
        PortObject.__init__(self)


    def SendMessageToUser(self,db,userID=None,message=None):
        """
        Sends a notification to user thru a desired medium
        @pre:    dbconn is the SQL database
            userID is the user to send the notification
            message is the message to send
        
        @post:    The message has been sent to user using his desired device
        """
        u= UserProfile.objects.get(user=userID)
        mail=u.email
          
        fromaddr = 'carpooling@gmail.com'  
        toaddrs  = 'mail'  
        username = 'username'  
        password = 'password'  
    
        server = smtplib.SMTP('smtp.gmail.com:587')  
        server.starttls()  
        server.login(username,password)  
        server.sendmail(fromaddr, toaddrs, message)  
        server.quit()  


    def routine(self,msg):
        """
    The only acceptable msg is ('newmsg',userID,strmessage)
    @pre : dbconn is initialized

           userID is the id of a user in the dbconn
           strmessage is a string

    @post : the send_message_to_user is called.
    """
        if msg[0]=='newmsg':
          try:
              userID=msg[1]
              message=msg[2]
              SendMessageToUser(db,userID,message)
          except:
            print "error newmsg"
