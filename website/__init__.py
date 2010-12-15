"""
import thread
from orbited import start

def listen():
  comet_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  comet_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  comet_socket.bind( ('', 9000) )
  comet_socket.listen(5)

  while 1:
     thread.start_new_thread(comet.handle_request, comet_socket.accept())

thread.start_new_thread(start.main, ())

thread.start_new_thread(listen, ())
"""
print "Car Pooling Server is now runing"

