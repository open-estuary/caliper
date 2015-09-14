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
        https://releases.linaro.org/14.09/components/toolchain/binaries/gcc-linaro-arm-linux-gnueabihf-4.9-2014.09_linux.tar.bz2 and https://releases.linaro.org/14.09/components/toolchain/binaries/gcc-linaro-aarch64-linux-gnu-4.9-2014.09_linux.tar.bz2.

    Export the tool chain path as necessary. An ideal way is to add the path in your .bashrc

3. Configuration
3.1 Target Configuration.
   Target ip to be configured in config/client_config.cfg.
   This part includes three sections. CLIENT is the information for Host to
   connect the Target. The SERVER is the host ip address which is used for
   connecting the Target. BMCER is used for rebooting the Target: the command is
   for rebooting the target; the host is the machine which it can execute the
       command; the user, port and password are used for logging the host. If
       you don’t want to record your password in the config file, you can copy
       the pubilc-key of Host to the target and the machine which execute the
       reboot command and put ‘None’ for the password field.

3.2 Configure the mail list
  Configure the config/email_config.cfg file to determine who will send and
  receive the mails, the mail contents will be the test reports.

  The email_info include the information of the mail, this includes the ‘From’,
  ‘To’, ‘Subject’ and ‘text’. The login_info is mainly for the user to login
  his/her mailbox to send test results. This section includes ‘user’, ‘password’
  and ‘server’. For 163 mailbox, the server address is ‘smtp.163.com’.

3.3 Configure the execution way
  This means when the processes of building and running occurred error, if caliper
will be stopped or not. The default value of the sections’ key are True.

3.4 Test tool selection
   test tool to be configured under test_cases_cfg/common_cases_def.cfg. To select
   the benchmarks you want to run, you need to 
   configure the config files located in test_cases_cfg/XXXX_cases_cfg.cfg(XXXX
   can be server, arm and common) to select the benchmarks you want to run. When
   you comment the corresponding sections in XXXX_cases_cfg.cfg, the tools won’t
   be selected.

3.5 Configure the test cases you want to run in a benchmark
  Configure the test_cases_cfg/XXXX/benchmark_name/benchmark_name_run.cfg(XXXX
  can be server, arm and common) files to select the test cases you want to run.
  When you comment the corresponding sections in benchmark_name_run.cfg, the
  test cases of the tools won’t be run.
 	
4. Test case compiling and execution
  you can use 'caliper -h' to see the commands caliper support.
    optional arguments:
      -h, --help     show this help message and exit
      -b, --build    select to build the selected test tools
      -B, --nobuild  select not to build process of test tools
      -r, --run      select to run the selected test tools
      -R, --norun    not to execute the process of running test tools
      -w, --webpage  select to generate the webpage test report
      -e, --email    Select to send mail to the receivers or not
      -f FOLDER, --folder FOLDER
                    assign a folder to store the results
      -c CONFIG_FILE, --config CONFIG_FILE
                    specify the location of config file

    '-b' is to build the selected test cases. The default value of it is True.

    '-B' is not to build the selected test cases, the default value of it is
    False.

    '-r' only includes running the test cases, it does not include the building
    process. The default value of it is 'False'.

    '-R' means not running the selected test cases. The default value of it is
    False.

    '-w' means will generate the webpage test report. It needs several sets of
    data. The default value is False.

    '-e' is selected to send test reports to the person which have been
    configured in the email_config.cfg . The default value is False.

    '-f': if you have installed caliper, the directory which is appointed to
    will be located in the ~/caliper_workspace; if not, the folder will be
    located in the root directory of caliper.


5. Log generation 
   Caliper framework gives an easy way to debug in case an error occurs during the process. All the log files are located in the folder which is specified by the '-f' options. If the '-f' option is not used, then the logs will be all located in the 'output_DIGIT' directory. THE DIGIT is a number which is increased automatically.

5.1 Build logs are captured under 
	caliper_build/tool_name_architecture.suc or   
	caliper_build/tool_name_architecture.fail
	*.suc - indicate that the tool compilation is successful
	*.fail - indicate that the tool compilation is failure

5.2 Executed test case result and parsed output files are  captured under
	caliper_exec/tool_output.log
	caliper_exec/tool_parser.log

5.3 Execution log 
      	caliper_exe.log - A detailed execution log with time stamp and duration in each steps have been created

5.4 A quick Execution summary
	results_summary.log - A quick summary of the current execution, the time for execution, target configuration, individual test case status etc has been written down in to this file.

6. Result 
	The graphs and final report file(in html) is created under results folder. 
	

********  Known limitation  ****************

1. Execution of multiple targets from same host is not supported.
2. configuring host as target as well is not supported.




 

