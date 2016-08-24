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

4. Updated the automation.cfg file with the required details.
		
5. Run the main.sh command with relevant parameters, run ./main.sh --help for details of different parameters.

Note: 
	1.If the toolchain is not downloaded then the script will download it by itself. 
