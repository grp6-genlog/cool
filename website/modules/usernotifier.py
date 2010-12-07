# @Author Group 6
# Interface of the UserNotifier module

from portobject import *

class UserNotifier(PortObject):
    

    def __init__(self):
        """
        Initialize the module
        @pre db is the SQL database of our system
        @post self.dbconn=db
              initialize the port object
        """
        PortObject.__init__(self)

    def SendMessageToUser(self,userID=None,message=None):
        """
        Sends a notification to user thru a desired medium
        @pre:userID is the user to send the notification
            message is the message to send
        
        @post:    The message has been sent to user using his desired device
        """
        pass


    def routine(self,msg):
        """
    The only acceptable msg is ('newmsg',userID,strmessage)
    @pre : userID is the id of a user in the dbconn
           strmessage is a string

    @post : the send_message_to_user is called.
    """
        pass
