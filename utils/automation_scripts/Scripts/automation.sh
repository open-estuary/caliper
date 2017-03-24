#!/bin/bash
# -*- coding:utf-8 -*-
#################################################
#   						#
#   Author  :   Dikshit N                       #
#   E-mail  :   dikshit.n@huawei.com	        #
#   Date    :   22/04/16 			#
#						#
#################################################

automationFile="../.automationconfig/automation_$1.cfg"
testFile="../testlist/testlist_$1"
copycfg="../Database_cfg/Database_$1"
server_def="/server_cases_def.cfg"
client_def="/common_cases_def.cfg"
wspath="$HOME/caliper_output/"
workspace=""
foldername=""
folder=""
checkDependency='y'
build_number=$2
copy=0

source helper_functions.sh


# read the options
if [ -f "$automationFile" ]
then
	autoSetupSystem=$( ini_get $automationFile TARGET autoSetupSystem  )
	checkDependency=$( ini_get $automationFile TARGET checkDependency  )
	Platform_name=$( ini_get $automationFile TARGET Platform_name )
	client_ip=$( ini_get $automationFile TARGET ip )
	server_ip=$( ini_get $automationFile TestNode ip )
	host_ip=$( ini_get $automationFile HOST ip )
	client_passwd=$( ini_get $automationFile TARGET password )
	server_passwd=$( ini_get $automationFile TestNode password )
	host_passwd=$( ini_get $automationFile HOST password )
	client_user=$( ini_get $automationFile TARGET user )
	server_user=$( ini_get $automationFile TestNode user )
	host_user=$( ini_get $automationFile HOST user ) 
	caliper_option=$( ini_get $automationFile TARGET caliper_option )
	mount_point=$( ini_get $automationFile TARGET mount_point )
else
	echo "$automationFile Does Not Exist"	
	exit 1
fi

autoSSH $client_user $client_ip $client_passwd
autoSSH $server_user $server_ip $server_passwd

echo -e " AutoSetupSystem=$autoSetupSystem\n checkDependency=$checkDependency \n Platform_name = $Platform_name \n server_user=$server_user\n server_ip=$server_ip\n server_passwd=$server_passwd\n client_user=$client_user\n client_ip=$client_ip\n client_passwd=$client_passwd\n caliper_option=$caliper_option\n Testlist = $testFile\n mount_point = $mount_point\n"

TEMP=`getopt -o o:dDcCh --long caliper_option:,check,dontcheck,copy,dontcopy,help -n 'automation.sh' -- "$@"`
if [ $? -ne 0 ]
then
	cat help.txt
	exit
fi

eval set -- "$TEMP"

# extract options and their arguments into variables.
while true ; do
    case "$1" in
        -o|--caliper_option)
	      caliper_option=$2
              lineNum=`cat $automationFile | grep "caliper_option" `	
	      sed -i "s/$lineNum/caliper_option\ =\ $caliper_option/g" $automationFile
	      shift 2 ;;
        -d|--check)
              checkDependency="y" ; shift;;
	-D|--dontcheck)
	      checkDependency="n" ; shift;;
	-c|--copy)
	      copy=1 ; shift;;
	-C|--dontcopy)
	      copy=0 ; shift;;
	-h|--help)
	     cat help.txt; shift; exit 1;;
        --) shift; break;;
        *) echo "Internal error!"; cat help.txt; exit 1 ;;
    esac
done

#checking all the test to be conducted

# writing into files automation
check_f_option=`echo $caliper_option | awk -F ' ' '{print $1}' | grep -c 'f'`
if [ $check_f_option -ne 0 ]
then
	list=(${caliper_option// / })
	folder=${list[1]}
fi

if [ -z $folder ] 
then
	echo "client ip = "$client_user@$client_ip	
	target_host=`ssh $client_user@$client_ip "hostname"`
	sleep 2
	TimeStamp=$(date "+%y-%m-%d_%H-%M-%S") 
	foldername=$(echo $target_host"_"$build_number )
	workspace=$wspath$target_host"_"$build_number
	
else
	folder=$( echo $folder"_"$build_number )
	workspace=$wspath$folder
	echo $workspace
	foldername=$folder
	list=(${caliper_option// / })
	cal_option=${list[0]}
	caliper_option=$(echo "$cal_option $folder" )
fi

if [[ ! -e $workspace ]]
then
    	mkdir $workspace
elif [[ ! -d $workspace ]]
then
    	echo "$workspace already exists but is not a directory" 1>&2
fi
`cp -r "$HOME/caliper_output/configuration/config" $workspace`
`cp -r "$HOME/caliper_output/configuration/test_cases_cfg" $workspace`

path="$workspace/test_cases_cfg"
server_def="$path$server_def"
client_def="$path$client_def"


if [ -f "$testFile" ]
then
	while read testline
	do
		if [ ${testline:0:1} != '#' -a -n $testline ]
		then
			uncomment $server_def $client_def $testline
		elif [ ${testline:0:1} == '#' ]
		then
			comment $server_def $client_def ${testline:1}
		fi
	done<$testFile
else
	echo "Error: $testfile File Does Not Exist. Check readme.txt for more information"	
	exit 1
fi

path_config="$workspace/config/client_config.cfg"
./modify.py "$path_config" "$client_ip" "$server_ip" "$Platform_name"
if [ $? -ne 0 ]
then
	echo "FAILED TO MODIFY $path_config"
	cat $path_config
	exit 1
fi

if [  -z $folder ] 
then
	caliper_option=$(echo $caliper_option"f $foldername")
fi	

#Comparing the tool chain
target_arch=`ssh $client_user@$client_ip "uname -a"`
target_arch=`echo $target_arch | awk -F ' ' '{print $12}'`
host_arch=`uname -a |  awk -F ' ' '{print $12}'`


#Exporting the Tool chain
echo "Target arch = $target_arch"
echo "Host arch = $host_arch"

if [ $target_arch != $host_arch ]
then
	
	target_arch=`ssh $client_user@$client_ip "uname -a"`
	target_arch=`echo $target_arch | awk -F ' ' '{print $13}'`
	
	checkCrossCompilation $target_arch $autoSetupSystem

	if [ $? -ne 0 ]
	then 
		exit 1
	fi
	echo "exporting $files_toolchain done"
fi

if [ "$checkDependency" == 'y' ]
then
	./server_dependency.exp "$autoSetupSystem" "$server_user" "$server_ip" "$server_passwd"
	if [ $? -eq 0 ]
	then
		echo "                      SERVER SUCESSFULL                                  "
	else
		echo "                      SERVER FAILED                                      "
	fi
	
	./host_dependency.exp "$autoSetupSystem" "$host_passwd"
	if [ $? -eq 0 ]
	then
		echo "                      HOST SUCESSFULL                                  "
	else
		echo "                      HOST FAILED                                      "
	fi

	./target_dependency.exp "$autoSetupSystem" "$client_user" "$client_ip" "$client_passwd" "$mount_point" 
fi

if [ $? -eq 0 ]
then
	echo -e "\n*********************************   Caliper is excuting   ***********************************\n"
	caliper $caliper_option 	 
	wait	
	echo -e "\n ********************************** caliper completed *****************************************\n"

else
	echo "Failed in Depenency"
    	exit 1
fi

if [ $copy -eq 1 ]
then
	./copy.sh "$copycfg" "$foldername" "$build_number"
fi
