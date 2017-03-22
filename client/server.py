#!/usr/bin/python
import socket                                         
import time
import subprocess
import sys
import os
import yaml
import logging
import signal
import fcntl

output_log = "/root/caliper_server/output_log"

try:
    subprocess.Popen(["iperf3","-s"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.Popen(["netserver"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
except Exception as e:
    fp = open(output_log,'w')
    fp.write("Error in starting Network sevices")
    fp.close()
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
    output_log = "/root/caliper_server/output_log"
    server_run = "/root/caliper_server/server_run"
    set_signals()

    if not os.path.exists(output_log):
        with SimpleFlock(output_log,60):
            f = open(output_log,'w')
            f.close()

    if not os.path.exists(server_run):
        with SimpleFlock(server_run,60):
            f = open(server_run,'w')
            f.close()
    
    p1 = subprocess.Popen(['ps','-ef'], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(['grep', '-c','server.py'], stdin=p1.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    data,err = p2.communicate()
    data = data.strip()
    print(data)
            
    if data != "2":
        with SimpleFlock(server_run,60):
            f = open(server_run,'w')
            f.write("server.py")
            f.close()
            sys.exit(0)
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
            f = open(output_log,'a')
            f.write("Got a connection from %s\n" % str(addr))
            f.close()
            currentTime = time.ctime(time.time()) + "\r\n"
            clientsocket.send("ACCESS GRANTED @ "+currentTime.encode('ascii'))
            f = open(output_log,'a')
            f.write("Waiting for %s to finish its task\n" % str(addr))
            f.close()
            clientsocket.recv(1024)
            f = open(output_log,'a')
            f.write("%s Completed its task\n"  % str(addr))
            f.close()
            clientsocket.close()
    except Exception as e:
	print e
        pass

    with SimpleFlock(process_status,60):                        
        fp = open(process_status,'w')                           
        fp.write('0')  
        fp.close()                                         
    reset_signals()
