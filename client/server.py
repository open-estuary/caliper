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

try:
    subprocess.Popen(["iperf3","-s"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.Popen(["netserver"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
except Exception as e:
    print "Error in starting Network sevices"
    print e
    sys.exit()

signal_ingored = [signal.SIGINT,signal.SIGTERM,signal.SIGALRM,signal.SIGHUP]
original_sigint = [None]*len(signal_ingored)
lock_yaml = "lock.yaml"

def exit_gracefully(signum, frame):
    # restore the original signal handler as otherwise evil things will happen
    # in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
    global original_sigint
    global signal_ingored
    global lock_yaml
    for i in range(len(signal_ingored)):
        signal.signal(signal_ingored[i], original_sigint[i])
    try:
        with SimpleFlock(lock_yaml,60):                             
            fp = open(lock_yaml,'w')                                
            dic = {"status":"0"}                                    
            fp.write(yaml.dump(dic,default_flow_style=False))       
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
    lock_yaml = 'lock.yaml'
    set_signals()
    if not os.path.exists(lock_yaml):
        with SimpleFlock(lock_yaml,60):
            fp = open(lock_yaml,'w')
            dic = {"status":0}
            fp.write(yaml.dump(dic,default_flow_style=False))
            fp.close()
    with SimpleFlock(lock_yaml,60):
        fp = open(lock_yaml,"r")
        dic = yaml.load(fp)
        if dic["status"] == 1 :
            print("server.py is already running")            
            p1 = subprocess.Popen(['ps','-ef'], stdout=subprocess.PIPE)
            p2 = subprocess.Popen(['grep','server.py'], stdin=p1.stdout, stdout=subprocess.PIPE)
            p3 = subprocess.Popen(['awk','-F', ' ','{print $2}'], stdin=p2.stdout, stdout=subprocess.PIPE)
            data = p3.communicate()
            data = str(data[0]).split("\n")
            count = 0
            
            for i in data:
                count = count + 1

            if count != 3:
                 sys.exit(0)
            else:
                 fp = open(lock_yaml,'w')
                 dic = {"status":0}
                 fp.write(yaml.dump(dic,default_flow_style=False))
                 fp.close()
        else:
	    fp.close()
            fp = open(lock_yaml,'w')
            dic["status"] = 1
            fp.write(yaml.dump(dic,default_flow_style=False))
        fp.close()
    try:
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
    
        while True:
            # establish a connection
            clientsocket,addr = serversocket.accept()      
            print("Got a connection from %s" % str(addr))
            currentTime = time.ctime(time.time()) + "\r\n"
            clientsocket.send("ACCESS GRANTED @ "+currentTime.encode('ascii'))
            print("Waiting for %s to finish its task" % str(addr))
            clientsocket.recv(1024)
            print("%s Completed its task"  % str(addr))
            clientsocket.close()
    except Exception as e:
	print e
        pass

    with SimpleFlock(lock_yaml,60):                        
        fp = open(lock_yaml,'w')                           
        dic = {"status":"0"}                               
        fp.write(yaml.dump(dic,default_flow_style=False))  
        fp.close()                                         
    reset_signals()
