#!/usr/bin/env python
# @Author Group 6
# Interface of the Tracker

from portobject import *
from django.contrib.auth.models import User
from offers.models import Offer
from rides.models import Ride
from proposals.models import Proposal
from requests.models import Request 
import socket,threading,datetime
from utils import get_distance
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
        TCP_IP = socket.gethostbyname(socket.gethostname()) # the car pooling tracker s
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

    def check_all_rides(self):
        """ dunno yet
        """
        new_connection = True
        # accept new connections and ask name
        while new_connection:
            try :
                conn,addr = self.tcp_socket.accept()
                print 'New unregistered user'
                conn.send('usr?&&\n')
                self.unregistered_connections.append((None,conn))
            except :
                new_connection = False
        # check if there is unregistered user to register
        self.lock.acquire()
        for unreg in self.unregistered_connections:
            try : 
                msg = unreg[1].recv(1024)
                if msg.split('&')[MTYPE]=='usr!':
                    if not User.objects.filter(username=msg.split('&')[MMESS]):
                        unreg[1].send('usr?&&\n')
                    else :
                        unreg[0]=msg.split('&')[MMESS]
                        conn.send('pwd?&&\n')
                elif msg.split('&')[MTYPE]=='pwd!':
                    try:
                        user = User.objects.get(username=unreg[0])
                        if user.check_password(msg.split('&')[MMESS]):
                            if unreg[0] not in self.userdict:
                                self.userdict[unreg[0]]=(unreg[1],list())
                                self.unregistered_connections.remove(unreg)
                            else:
                                self.userdict[unreg[0]][UCONN]=unreg[1]
                        else :
                            unreg[1].send('pwd?&&\n')
                    except:                      
                        unreg[1].send('usr?&&\n')
            except : 
                pass
        self.lock.release()

        # check for each ride if there's something to do
        for ride in self.rides_list:
            if not ride[NDAWARE] and ride[NDRIVER] in self.userdict:
                self.userdict[NDRIVER][0].send('ndr!&&\n')
                ride[NDAWARE]=True
            if ride[STATE]==SPENDING and (ride[RIDETIME]-datetime.datetime.now()) < datetime.timedelta(0,60*30):
                # the driver has to be notified
                self.send_to(self.usernotifier_port,('newmsg',ride[DRIVER],"Don't forget your ride from "
                                                     +str(ride[RIDETIME])))
                ride[STATE]=SREMINDED
            if (ride[STATE]==SREMINDED or ride[STATE]==SOPENCONN) and (ride[RIDETIME]-datetime.datetime.now())<datetime.timedelta(0,60*5):
                # the nondriver should be asked if the ride has started
                if ride[NDRIVER] in self.userdict:
                    self.userdict[ride[NDRIVER]].send('stt?&'+str(ride[RIDEID])+'&'+str(ride[RIDETIME])+'\n')
                    ride[STATE]=SSTARTEDA
                elif ride[STATE]==SREMINDED:
                    self.send_to(self.usernotifier_port,('newmsg',ride[NDRIVER],"Please, open your COOL's smartphone app."))
                    ride[STATE]=SOPENCONN
            
            if ride[DRIVER] in self.userdict:
                fill_buffer(self.userdict[ride[DRIVER]])
                for msg in self.userdict[ride[DRIVER]][UBUFF]:
                    if msg.split('&')[MTYPE]=='est!' and int(msg.split('&')[MRIDE])==ride[RIDEID]:
                        self.userdict[ride[DRIVER]][UBUFF].remove(msg)
                        if ride[NDRIVER] not in self.userdict:
                            self.send_to(self.usernotifier_port,('newmsg',ride[NDRIVER],"Please, open your COOL's smartphone app."))
                        else:
                            self.userdict[ride[NDRIVER]][UCONN].send(msg)
                    elif msg.split('&')[MTYPE]=='pos!' and int(msg.split('&')[MRIDE])==ride[RIDEID]:
                        self.userdict[ride[DRIVER]][UBUFF].remove(msg)
                        if ride[NDRIVER] not in self.userdict:
                            self.send_to(self.usernotifier_port,('newmsg',ride[NDRIVER],"Please, open your COOL's smartphone app."))
                        else:
                            dist = get_distance(map(float,msg.split('&')[MMESS].split()),(ride[PPLAT],ride[PPLON]))
                            self.userdict[ride[NDRIVER]][UCONN].send('dst!&'+msg[MRIDE]+'&'+str(dist)+' km\n')
                    else:
                        print 'connection with ',ride[DRIVER],'closed.'
                        self.userdict[ride[NDRIVER]][UCONN].close()
                        self.userdict[ride[NDRIVER]][UCONN]=None
                if userdic[ride[DRIVER]]==(None,list()):
                    # erase the connection
                    pass

            if ride[NDRIVER] in self.userdict:
                fill_buffer(self.userdict[ride[NDRIVER]])
                for msg in self.userdict[ride[NDRIVER]][UBUFF]:
                    if msg.split('&')[MTYPE]=='est?' and int(msg.split('&')[MRIDE])==ride[RIDEID]:
                        self.userdict[ride[DRIVER]][UBUFF].remove(msg)
                        if ride[DRIVER] not in self.userdict:
                            self.send_to(self.usernotifier_port,('newmsg',ride[DRIVER],"Please, open your COOL's smartphone app."))
                            self.userdict[ride[NDRIVER]][UCONN].send('dnc!&&\n')
                        else:
                            if ride[MANUAL_MODE]:
                                self.userdict[ride[DRIVER]][UCONN].send('est?&'+str(ride[RIDEID])+'&'+str(ride[RIDETIME])+'\n')
                            else:
                                self.userdict[ride[DRIVER]][UCONN].send('pos?&&\n')
                    elif msg.split('&')[MTYPE]=='stt!' and int(msg.split('&')[MRIDE])==ride[RIDEID]:
                        self.userdict[ride[DRIVER]][UBUFF].remove(msg)
                        threading.Thread(target=ride[CALLB_OK]).start()
                        print 'ride ok'
                        rides_list.remove(ride)
                    elif msg.split('&')[MTYPE]=='ccl!' and int(msg.split('&')[MRIDE])==ride[RIDEID]:
                        self.userdict[ride[DRIVER]][UBUFF].remove(msg)
                        threading.Thread(target=ride[CALLB_KO]).start()
                        print 'ride cancelled'
                        rides_list.remove(ride)
                    else:
                        print 'connection with ',ride[DRIVER],'closed.'
                        self.userdict[ride[NDRIVER]][UCONN].close()
                        self.userdict[ride[NDRIVER]][UCONN]=None
                if userdic[ride[DRIVER]]==(None,list()):
                    # erase the connection
                    pass                           
        threading.Timer(5.,lambda:self.check_all_rides()).start()

    def routine(self,msg):
        """
        There is two messages received by tracker : 
        ('startride',instruID,callb_ok,callb_ko)
        @pre : instruId is the id of an instruction (ride) in DB
        @post : start_ride is called.
        """
        if msg[0]:
            ride = Ride.objects.get(id=msg[1])
            driver = ride.offer.proposal.user
            ndriver = ride.offer.request.user
            lock.acquire()
            info = (msg[1],datetime.datetime(offer.pickup_time),False,msg[2],msg[3],driver,ndriver,SPENDING,offer.pickup_point_lat,offer.pickup_point_long,False)
            rides_list.append(info)
            if ndriver in self.userdict:
                self.userdict[ndriver][0].send('ndr!&&\n')
                info[NDAWARE]=True
            lock.release()
            
            
    
