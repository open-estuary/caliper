#!/usr/bin/python
import re
import sys
import pdb

def check_status(content):
	
	for line in content:
		if re.match("(.*?) : Build Fail", line):
			print(line)
		if re.match("(.*?) : Execution Partial PASS", line):
			print(line)
		if re.match("(.*?) : Execution Fail", line):
			print(line)

if __name__ == "__main__":
	fp = open(sys.argv[1], "r")
	check_status(fp)
	fp.close()    
