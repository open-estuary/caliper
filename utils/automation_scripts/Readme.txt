Description
This is a utility script to execute caliper and do caliper dependancy check and installation in host and target. 
This file can be used to automate caliper execution. This is not part of caliper framework but just the helper scripts for automation.

Instruction:
1. Make sure you create a folder in your home directory and name it as "toolchain" and keep required toolchain files in this folder.
2. "testlist.txt" file contains a list of test to be performed by caliper, put an '#' symbol before the test name you wish to not execute
    For example 
	#[tinymembench]
	#[openssl]
	[coremark]
	#[scimark]		   
	#[linpack]
	 [hadoop]

This will not execute tinymembench, openssl, scimark and linpack	
		
3. Run the main.sh command with the following arguments
   option=$1
   server_id=$2
   server_ip=$3
   server_passwd=$4
   client_id=$5
   client_ip=$6
   client_passwd=$7
   caliper_option=$8
 
   Examples:
   ./main.sh " " "XYZ" "192.168.40.156" "xyz" "root" "192.168.40.27" "root123" "-br"
   here,
   option = " "  #this can be given as -f to automatically install all the dependency without asking the user, if you leave it blank then it will ask the user each time it has to make any changes 
   server_id= XYZ  #Sudo user name in the server machine
   server_ip= 192.168.40.156	#IP of the server machine
   server_passwd= xyz		#Password for that user in the server machine
   client_id=root
   client_ip=192.168.40.27
   client_passwd=root123
   caliper_option=-br
