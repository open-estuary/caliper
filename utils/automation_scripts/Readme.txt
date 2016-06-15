Description
This is a utility script to execute caliper and do caliper dependancy check and installation in host and target. 
This file can be used to automate caliper execution. This is not part of caliper framework but just the helper scripts for automation.

Instruction:
1. Download and keep the required toolchains in the "toolchain".

2. Download the following packages on your target machine manually as the script will not be able to install it automatically.
	-sudo apt-get install mysql-server
	-sudo apt-get install libmysqlclient-dev

3. "testlist.txt" file contains a list of test to be performed by caliper, put an '#' symbol before the test name you wish to not execute
    For example 
	#[tinymembench]
	#[openssl]
	[coremark]
	#[scimark]		   
	#[linpack]
	[hadoop]

This will not execute tinymembench, openssl, scimark and linpack	
		
4. Run the main.sh command with the following arguments
   ./main.sh <option> <server_id> <server_ip> <server_passwd> <client_id> <client_ip> <client_passwd> <caliper_option>
   here,

   option = -f or " " #Force install all dependency or ask user everytime it install any dependency
   server_id=  #Sudo user name in the server machine
   server_ip= 	#IP of the server machine
   server_passwd=  #Password for that user in the server machine
   client_id= #Sudo user name in the target machine
   client_ip= #IP of the target machine
   client_passwd= #Password for that user in the target machine
   caliper_option= #options for caliper

  Note: 
  	1.Option field can be given as -f to automatically install all the dependency without asking the user, if you leave it blank then it will ask the user each time it has to make any changes 
	2.If the toolchain is not downloaded then the script will download it by itself. 
