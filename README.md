******   Quick ReadMe to get started   ******
Specific to 1.01

Caliper test suite mainly includes performance test cases which can be used to test the performance of a Linux machine.
The test suite supports x86_64, arm_32 and arm_64. 

Steps to run Caliper

1. Host OS installation
    It supports x86_64 CentOS6 and Ubuntu platform, you need install 64bit
    CentOS system or Ubuntu system on your PC or server platform.

2. Toolchain installation
    To build arm/android target binary, it requires arm toolchain deployment, for arm system we use compiler with hard-float ABI. 

    Here is website to download ARM toolchains:
        https://releases.linaro.org/13.10/components/toolchain/binaries/gcc-linaro-arm-linux-gnueabihf-4.8-2013.10_linux.tar.bz2
    Export the tool chain path as necessary. An ideal way is to add the path in your .bashrc
3. Target Configuration.
   Target ip to be configured in config/client_config.cfg 	
   This ip should be configured for autolog in

4. Test tool selection
   test tool to be configured under test_cases_cfg/common_cases_def.cfg
 	
5. Test case compiling and execution
   Caliper release 1.01-rc has combined caliper test case compiling and execution to a single command.
   The execution file is located at the root folder named as caliper
   Once you run the caliper the following steps happens
6.1 Compile the available test cases and copy the binaries to /binaries folder under respective architecture
6.2 Copy the compiled binaries to target system and execute the binaries there.
6.3 Capture the test result from each tools and copy it back to host
6.4 Run parser on the test result logs and capture parameters of interest, normalise, score and create the yaml file as per the test classification
6.5 Generate a report html file (basic) with the results from executed target.

7. Log generation 
   Caliper framework gives an easy way to debug in case an error occurs during the process.

7.1 Build logs are captured under 
	caliper_build/tool_name_architecture.suc or   
	caliper_build/tool_name_architecture.fail
	*.suc - indicate that the tool compilation is successful
	*.fail - indicate that the tool compilation is failure

7.2 Executed test case result and parsed output files are  captured under
	caliper_exec/tool_output.log
	caliper_exec/tool_parser.log

7.3 Execution log 
      	caliper_exe.log - A detailed execution log with time stamp and duration in each steps have been created

7.4 A quick Execution summary
	results_summary.log - A quick summary of the current execution, the time for execution, target configuration, individual test case status etc has been written down in to this file.

8. Result 
	The graphs and final report file(in html) is created under results folder. 
	

********  Known limitation  ****************

1. Execution of multiple targets from same host is not supported.
2. configuring host as target as well is not supported.




 

