#!/usr/bin/python
import socket                                         
import time
import subprocess
import sys
import os
import logging
import signal
import fcntl

try:
    subprocess.Popen(["iperf3","-s"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.Popen(["netserver"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.Popen(["qperf"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
except Exception as e:
    print e
    sys.exit()

signal_ingored = [signal.SIGINT,signal.SIGTERM,signal.SIGALRM,signal.SIGHUP]
original_sigint = [None]*len(signal_ingored)
process_status = "/root/caliper_server/process_status"

def exit_gracefully(signum, frame):
    # restore the original signal handler as otherwise evil things will happen
    # in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
    global original_sigint
    global signal_ingored
    global process_status
    for i in range(len(signal_ingored)):
        signal.signal(signal_ingored[i], original_sigint[i])
    try:
        with SimpleFlock(process_status,60):                            
            fp = open(process_status, 'w')
            fp.write('0')
            fp.close()

    except Exception as e:
        logging.error(e)
    sys.exit(1)

    # restore the exit gracefully handler here
    # signal.signal(signal.SIGINT, exit_gracefully)

def set_signals():
    global original_sigint
    global signal_ingored 
    for i in range(len(signal_ingored)):
        original_sigint[i] = signal.getsignal(signal_ingored[i])
        signal.signal(signal_ingored[i], exit_gracefully)

def reset_signals():                                     
    global original_sigint                               
    global signal_ingored                                
    for i in range(len(signal_ingored)):                 
        signal.signal(signal_ingored[i], signal.SIG_DFL) 

class SimpleFlock:
   def __init__(self, path, timeout = None):
      self._path = path
      self._timeout = timeout
      self._fd = None

   def __enter__(self):
      self._fd = os.open(self._path,os.O_CREAT)
      start_lock_search = time.time()
      while True:
         try:
            fcntl.flock(self._fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            # Lock acquired!
            return self._fd
         except (OSError, IOError) as ex:
            if ex.errno != errno.EAGAIN: # Resource temporarily unavailable
               print(ex)
               raise
            elif self._timeout is not None and time.time() > (start_lock_search + self._timeout):
               # Exceeded the user-specified timeout.
               print("TIMEOUT")
               raise
         time.sleep(0.1)

   def __exit__(self, *args):
      fcntl.flock(self._fd, fcntl.LOCK_UN)
      os.close(self._fd)
      self._fd = None

if __name__ == "__main__":
    process_status = "/root/caliper_server/process_status"

    set_signals()

    try:
        if not os.path.exists(process_status):
            with SimpleFlock(process_status,60):
                fp = open(process_status,'w')
                fp.write('0')
                fp.close()

        # create a socket object
        serversocket = socket.socket(
                        socket.AF_INET, socket.SOCK_STREAM) 
        # get local machine name
        host = ''                           
        
        port = int(sys.argv[1])                                          
        
        # bind to the port
        serversocket.bind((host, port))                                  
        
        # queue up to 5 requests
        serversocket.listen(5)

        with SimpleFlock(process_status,60):
            fp = open(process_status, 'w')
            fp.write('1')
            fp.close()

        while True:
            # establish a connection
            clientsocket,addr = serversocket.accept()
            print("Got a connection from %s" % str(addr))
            currentTime = time.ctime(time.time()) + "\r\n"
            clientsocket.send("ACCESS GRANTED @ "+currentTime.encode('ascii'))
	    print("Waiting for %s to finish its task" % str(addr))
            clientsocket.recv(1024)
	    print("%s Completed its task" % str(addr))
            clientsocket.close()

    except Exception as e:
	print e
        pass

    with SimpleFlock(process_status,60):
        fp = open(process_status,'w')
        fp.write('0')
        fp.close()
    reset_signals()
