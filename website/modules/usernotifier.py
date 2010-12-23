# @Author Group 6
# Interface of the UserNotifier module

from portobject import *
import traceback

from website.profiles.models import UserProfile

from django.core.mail import send_mail


class UserNotifier(PortObject):
    fromaddr = 'carpooling.cool@gmail.com'
    server = None

    def __init__(self):
        """ Initialize the port object """
        PortObject.__init__(self)
        

    def SendMessageToUser(self,userID=None,message=None):
        """
        Sends a notification to user thru a desired medium
        @pre: userID is the user to send the notification
              message is the message to send
        
        @post: The message has been sent to user using his desired device
        """
        u = UserProfile.objects.get(id=userID)
        mail = u.user.email
        send_mail('Car pooling notification', message, 'carpooling.cool@gmail.com',[mail], fail_silently=False)
        print "mail sent to "+mail

    def routine(self,src,msg):
        """
        The only acceptable msg is ( newmsg ,userID,strmessage)
        @pre : userID is the id of a user in the dbconn
        strmessage is a string
        @post : the send_message_to_user is called.
        """

        if msg[0]=='newmsg':
            userID=msg[1]
            message=msg[2]
            self.SendMessageToUser(userID,message)
        else:
            print "message unknown : "+str(msg[0])
