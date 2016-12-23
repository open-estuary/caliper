#!/usr/bin/python
import paramiko
import os
import time
import sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(sys.argv[1], username=sys.argv[2], password=sys.argv[3], timeout=1)
try:
	stdin, stdout, stderr = ssh.exec_command("/sbin/reboot -f > /dev/null 2>&1 &")
	time.sleep(360)
	hostname = sys.argv[1] 
	response = os.system("ping -c 1 " + hostname)
	#and then check the response...
	if response == 0:
		print hostname, 'is up!'
	else:
		print hostname, 'is down!'
except AuthenticationException, e:
	print ''
finally:
	time.sleep(120)
	ssh.close()
