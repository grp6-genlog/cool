#!/usr/bin/env python

import socket,sys,pickle,threading,re
from gps import *

print 21*'#'
print ' Car Pooling App 2.0'
print 21*'#'

if len(sys.argv)>3 or len(sys.argv)<2:
    print 'default usage:',sys.argv[0],'<Car Pooling Server IP> <GPS FILE> (optional)'
    sys.exit(1)

TCP_IP = sys.argv[1] # the car pooling tracker 'IP
TCP_PORT = 4242 # and port
BUFFER_SIZE = 1000
ride_number=None

GPS_coord = None
if len(sys.argv)==3:
    f_in = open(sys.argv[2])
    GPS_coord = pickle.load(f_in)
    f_in.close()


s = [socket.socket(socket.AF_INET, socket.SOCK_STREAM)]
s[0].connect((TCP_IP, TCP_PORT))


def routine(conn,list_msg,lock):
    while True:
        msgs = conn[0].recv(BUFFER_SIZE)
        if not msgs:
            break
        for data in msgs.split('\n'):
            if data.split('&')[0]=='usr?':
                lock.acquire()
                list_msg.append(('USER LOGIN','usr?'))
                lock.release()
                print len(list_msg),'USER LOGIN'
            elif data.split('&')[0]=='pwd?':
                lock.acquire()
                list_msg.append(('PASSWORD','pwd?'))
                lock.release()
                print len(list_msg),'PASSWORD'
            elif data.split('&')[0]=='ndr!':
                lock.acquire()
                text = 'GET INFORMATION ABOUT DRIVER FOR THE RIDE OF '+str(data.split('&')[2])
                text1 = 'DECLARE RIDE STARTED FOR THE RIDE OF '+str(data.split('&')[2])
                text2 = 'CANCEL RIDE OF '+str(data.split('&')[2])
                list_msg.append((text,'get?&'+data.split('&')[1]+'&\n'))
                list_msg.append((text1,'stt!&'+data.split('&')[1]+'&\n'))
                list_msg.append((text2,'ccl!&'+data.split('&')[1]+'&\n'))
                lock.release()
                print len(list_msg)-2,text
                print (len(list_msg)-1),text1
                print len(list_msg),text2
                
            elif data.split('&')[0]=='get?':
                if GPS_coord:
                    coord = GPS_coord.get_coord()
                    conn[0].send('pos!&'+data.split('&')[1]+'&'+str(coord[0])+' '+str(coord[1])+'\n')
                else: 
                    lock.acquire()
                    list_msg.append(('ESTIMATE POSITION FOR RIDE OF '+data.split('&')[2],'est!&'+data.split('&')[1]))
                    lock.release()
                    print len(list_msg),'ESTIMATE POSITION FOR RIDE '
            elif data.split('&')[0]=='dst!':
                print "!!! Driver's distance to pick up point:",data.split('&')[2],'!!!'
            elif data.split('&')[0]=='dnc!':
                print "!!! Please wait a bit : driver is not connected for the moment. !!!"
            elif data.split('&')[0]=='est!':
                print "!!! Driver's personnal estimation:",data.split('&')[2],'!!!'
            elif data.split('&')[0]=='stt!':
                print "!!! Ride "+data.split('&')[1]+'has started !!!'
            elif data.split('&')[0]=='stt?':
                print "!!! ride time is close : don't forget to declare the ride has started in due time !!!"
    s[0].close()

list_msg = list()
lock = threading.Lock()

threading.Thread(target=routine,args=(s,list_msg,lock,)).start()

user = raw_input('User login: ')
s[0].send('usr!&&'+user+'\n')

def printall(l):
    for i in xrange(len(l)):
        print i+1,l[i][0]

lock.acquire()
while True:
    threading.Timer(0.1,lambda:printall(list_msg)).start()
    lock.release()
  
    data=int(re.sub('[^0-9]','',raw_input("Enter your choice's index in the list below:\n")))
    lock.acquire()
    msg = list_msg[data-1][1].split('&')
    if msg[0]=='usr?':
        username = raw_input('Username:')
        list_msg.remove(list_msg[data-1])
        s[0].send('usr!&&'+username+'\n')
    elif msg[0]=='pwd?':
        password = raw_input('Password:')
        list_msg.remove(list_msg[data-1])
        s[0].send('pwd!&&'+password+'\n')
    elif msg[0]=='est!':
        s[0].send('est!&'+msg[1]+'&'+raw_input('Estimate time before arrival for ride '+msg[1]+' ? ')+'\n')
        list_msg.remove(list_msg[data-1])
    elif msg[0]=='get?':
        s[0].send(list_msg[data-1][1])
    elif msg[0]=='stt!':
        s[0].send(list_msg[data-1][1])
        s[0].close()
        lock.release()
        sys.exit(0)
    elif msg[0]=='ccl!':
        s[0].send(list_msg[data-1][1])        
        s[0].close()
        lock.release()
        sys.exit(0)
    else:
        s[0].close()



