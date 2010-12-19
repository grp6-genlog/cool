#!/usr/bin/env python
# @Author Group 6
# Interface of the Tracker

DEBUG=False

from portobject import *

if not DEBUG:
    from django.contrib.auth.models import User
    from offers.models import Offer
    from rides.models import Ride
    from proposals.models import Proposal
    from requests.models import Request
    from profiles.models import UserProfile
import socket,threading,datetime
from utils import get_distance

DERIDEND=0
DERIDED=1
DERIDEPUPT=2
DERIDEPUPLON=3
DERIDEPUPLAT=4

RIDEID=0
RIDETIME=1
MANUAL_MODE=2
CALLB_OK=3
CALLB_KO=4
DRIVER=5
NDRIVER=6
STATE =7
PPLAT=8
PPLON=9
NDAWARE=10

SPENDING=0 # ride state for 'not yet started'
SREMINDED=1 # ride state for 'ride reminded'
SOPENCONN=2 # ride state for 'non driver asked to add money'
SSTARTEDA=3 # ride state for 'ride started ?'

UCONN=0 # the user associated connection
UBUFF=1 # the current messages buffer associate to the user

MTYPE=0
MRIDE=1
MMESS=2

def fill_buffer(userconn):
    msgs = ''
    while True:
        try:
            msgs+=userconn[UCONN].recv(4096)
        except:
            break
    userconn[UBUFF].extend(filter(lambda(X):X!='',msgs.split('\n')))
    
class Tracker(PortObject):
    rides_list = None # the list of all rides currently observed. A ride is a set(rideid,ridestart,manual_mode,callb_ok
                      #                                                         ,callb_ko,driver,ndriver,state,lat,lon).
    
    unregistered_connections = None # list of pair (username (or None),conn)
    userdict = None # a dictionary with triplet (conn,msgbuff)
    usernotifier_port = None # the port of the UserNotifier module
    lock = None # the lock of internal datastructures
    tcp_socket = None # the socket
    
    debug_userlist = ['remy','fx','cycy']
    debug_userdico = {'remy':'pass','fx':'password','cycy':'test'}
    debug_rides = {'1234':(1,0,datetime.datetime(2010,12,19,11,45),4.0,5.0),'1235':(2,0,datetime.datetime(2010,12,19,11,50),4.0,5.0)}

    def __init__(self,usernotifier_port):
        """
        Initialize self structures.
        @pre : usernotifier_port is the port of the UserNotifier module
        @post : rides_list=list() initialized as an empty list
                self.usernotifier_port=usernotifier_port
                lock is a released lock
                the port_object init has been called called
        """
        self.usernotifier_port = usernotifier_port
        TCP_IP = "130.104.99.183" # the car pooling tracker s
        TCP_PORT = 4242 # and port
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.bind((TCP_IP,TCP_PORT))
        self.tcp_socket.listen(50000)
        self.tcp_socket.setblocking(0)
        self.userdict = dict()
        self.unregistered_connections = list()
        self.lock = threading.Lock()
        self.rides_list = list()
        self.check_all_rides()
        PortObject.__init__(self)
    def check_all_rides(self):
        """ dunno yet
        """
        new_connection = True
        # accept new connections and ask name
        while new_connection:
            try :
                conn,addr = self.tcp_socket.accept()
                print 'New unregistered user'
                conn.setblocking(0)
                self.unregistered_connections.append([None,conn])
            except :
                new_connection = False
        # check if there is unregistered user to register
        self.lock.acquire()
        for unreg in self.unregistered_connections:
            try : 
                msgs = unreg[1].recv(1024)
                for msg in msgs.split('\n'):
                    print msg.split('&')[MTYPE]
                    if msg.split('&')[MTYPE]=='usr!':
                        print 'log',msg.split('&')[MMESS]
                        if not User.objects.filter(username=msg.split('&')[MMESS]):#msg.split('&')[MMESS] not in self.debug_userdico:
#
                            print 'not in dic'
                            unreg[1].send('usr?&&\n')
                        
                        else :
                            unreg[0]=msg.split('&')[MMESS]
                            print 'in dic'
                            unreg[1].send('pwd?&&\n')
                    
                    elif msg.split('&')[MTYPE]=='pwd!':
                        try:
                            user = None
                            if not DEBUG:
                                user = User.objects.get(username=unreg[0])
                            if user.check_password(msg.split('&')[MMESS]):#self.debug_userdico[unreg[0]]==msg.split('&')[MMESS]:
# 
                                if unreg[0] not in self.userdict:
                                    self.userdict[unreg[0]]=[unreg[1],list()]
                                    self.unregistered_connections.remove(unreg)
                                else:
                                    self.userdict[unreg[0]][UCONN]=unreg[1]
                            else :
                                unreg[1].send('pwd?&&\n')
                        except:                      
                            unreg[1].send('usr?&&\n')
            except socket.error : 
                pass
        self.lock.release()

        # check for each ride if there's something to do
        for ride in self.rides_list:
            drivername = None
            if DEBUG:
                drivername = self.debug_userlist[ride[DRIVER]]
            else:
                drivername = UserProfile.objects.get(id=ride[DRIVER]).user.username

            ndrivername = None
            if DEBUG:
                ndrivername = self.debug_userlist[ride[NDRIVER]]
            else:
                ndrivername = UserProfile.objects.get(id=ride[NDRIVER]).user.username

            if not ride[NDAWARE] and ndrivername in self.userdict:
                self.userdict[ndrivername][0].send('ndr!&'+str(ride[RIDEID])+'&'+str(ride[RIDETIME])+'\n')
                ride[NDAWARE]=True
            if ride[STATE]==SPENDING and (ride[RIDETIME]-datetime.datetime.now()) < datetime.timedelta(0,60*30):
                # the driver has to be notified
                self.send_to(self.usernotifier_port,('newmsg',ride[DRIVER],"Don't forget your ride from "
                                                     +str(ride[RIDETIME])))
                ride[STATE]=SREMINDED
            if (ride[STATE]==SREMINDED or ride[STATE]==SOPENCONN) and (ride[RIDETIME]-datetime.datetime.now())<datetime.timedelta(0,60*5):
                # the nondriver should be asked if the ride has started
                if ndrivername in self.userdict:
                    self.userdict[ndrivername][UCONN].send('stt?&'+str(ride[RIDEID])+'&'+str(ride[RIDETIME])+'\n')
                    ride[STATE]=SSTARTEDA
                elif ride[STATE]==SREMINDED:
                    self.send_to(self.usernotifier_port,('newmsg',ride[NDRIVER],"Please, open your COOL's smartphone app."))
                    ride[STATE]=SOPENCONN
        

            

            if drivername in self.userdict:
                fill_buffer(self.userdict[drivername])
                for msg in self.userdict[drivername][UBUFF]:
                    print msg
                    if msg.split('&')[MTYPE]=='est!' and int(msg.split('&')[MRIDE])==ride[RIDEID]:
                        self.userdict[drivername][UBUFF].remove(msg)
                        if drivername not in self.userdict:
                            self.send_to(self.usernotifier_port,('newmsg',ride[NDRIVER],"Please, open your COOL's smartphone app."))
                        else:
                            self.userdict[ndrivername][UCONN].send(msg)
                    elif msg.split('&')[MTYPE]=='pos!' and int(msg.split('&')[MRIDE])==ride[RIDEID]:
                        self.userdict[drivername][UBUFF].remove(msg)
                        if ndrivername not in self.userdict:
                            self.send_to(self.usernotifier_port,('newmsg',ride[NDRIVER],"Please, open your COOL's smartphone app."))
                        else:
                            dist = get_distance(map(float,msg.split('&')[MMESS].split()),(ride[PPLAT],ride[PPLON]))
                            self.userdict[ndrivername][UCONN].send('dst!&'+msg[MRIDE]+'&'+str(dist)+' km\n')
                    else:
                        print 'connection with ',ride[DRIVER],'closed.'
                        self.userdict[drivername][UCONN].close()
                        self.userdict[drivername][UCONN]=None
                if self.userdict[drivername]==[None,list()]:
                    # erase the connection
                    pass

                        
            if ndrivername in self.userdict:
                fill_buffer(self.userdict[ndrivername])
                for msg in self.userdict[ndrivername][UBUFF]:
                    print msg
                    if msg.split('&')[MTYPE]=='get?' and int(msg.split('&')[MRIDE])==ride[RIDEID]:
                        self.userdict[ndrivername][UBUFF].remove(msg)
                        if drivername not in self.userdict:
                            self.send_to(self.usernotifier_port,('newmsg',ride[DRIVER],"Please, open your COOL's smartphone app."))
                            self.userdict[ndrivername][UCONN].send('dnc!&&\n')
                        else:
                            self.userdict[drivername][UCONN].send('get?&'+str(ride[RIDEID])+'&'+str(ride[RIDETIME])+'\n')
                            
                    elif msg.split('&')[MTYPE]=='stt!' and int(msg.split('&')[MRIDE])==ride[RIDEID]:
                        self.userdict[ndrivername][UBUFF].remove(msg)
                        threading.Thread(target=ride[CALLB_OK]).start()
                        if drivername in self.userdict:
                            self.userdict[drivername][UCONN].send('stt!&'+str(ride[RIDEID])+'&\n')
                        else:
                            self.send_to(self.usernotifier_port,('newmsg',ride[DRIVER],'Ride '+str(ride[RIDEID])+' has started.'))
                        print 'ride ok'
                        self.rides_list.remove(ride)
                    elif msg.split('&')[MTYPE]=='ccl!' and int(msg.split('&')[MRIDE])==ride[RIDEID]:
                        self.userdict[ndrivername][UBUFF].remove(msg)
                        threading.Thread(target=ride[CALLB_KO]).start()
                        print 'ride cancelled'
                        self.rides_list.remove(ride)
                    else:
                        print 'connection with ',ride[DRIVER],'closed.'
                        self.userdict[drivername][UCONN].close()
                        self.userdict[ndrivername][UCONN]=None
                if self.userdict[ndrivername]==(None,list()):
                    # erase the connection
                    pass
        threading.Timer(5.,lambda:self.check_all_rides()).start()

    def routine(self,src,msg):
        """
        There is two messages received by tracker : 
        ('startride',instruID,callb_ok,callb_ko)
        @pre : instruId is the id of an instruction (ride) in DB
        @post : start_ride is called.
        """
        print msg
        if msg[0]=='startride':
            ride,driver,ndriver=None,None,None
            if not DEBUG:
                ride = Ride.objects.get(id=msg[1])
                driver = ride.offer.proposal.user.id
                ndriver = ride.offer.request.user.id
            else:
                ride = self.debug_rides[str(msg[1])]
                ndriver = ride[DERIDEND]
                driver = ride[DERIDED]
            
            self.lock.acquire()

            info = None
            if DEBUG:
                info = [msg[1],ride[DERIDEPUPT],False,msg[2],msg[3],driver,ndriver,SPENDING,ride[DERIDEPUPLAT],ride[DERIDEPUPLON],False]
            else:
                info = [msg[1],ride.offer.pickup_time,False,msg[2],msg[3],driver,ndriver,SPENDING,ride.offer.pickup_point.latitude,ride.offer.pickup_point.longitude,False]
            
            self.rides_list.append(info)
            if ndriver in self.userdict:
                self.userdict[ndriver][0].send('ndr!&&\n')
                info[NDAWARE]=True
            self.lock.release()
        elif msg[0]=='cancelride':
            self.lock.acquire()
            for ride in self.rides_list:
                if ride[RIDEID]==msg[1]:
                    self.rides_list.remove(ride)
            self.lock.release()
        
