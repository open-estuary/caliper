#!/bin/bash
# -*- coding:utf-8 -*-
#
#   Author  :   Dikshit N
#   E-mail  :   dikshit.n@huawei.com
#   Date    :   22/04/16 
#
path="$HOME/caliper_output/configuration/test_cases_cfg/"
path_config="$HOME/caliper_output/configuration/config/client_config.cfg"
automationFile="automation.cfg"
testFile="testList"
server_def="$path/server_cases_def.cfg"
client_def="$path/common_cases_def.cfg"
clear
comment()
{
	#finding the pattern in server file
	fileName=$server_def
	line=`cat "$fileName" | grep -Fn "$1"`

	#checking if the pattern is in server file
	if [ -z $line ]
	then
		#finding the pattern in server file
		fileName=$client_def
		line=`cat "$client_def" | grep -Fn "$1"`
	fi
	
	#extracting the line num and the pattern of the test
	num=`echo "$line" | awk -F : '{ print $1 }'`
	string=`echo "$line" | awk -F : '{ print $2 }'`
	num2=$(($num+3))

	if [ ${string:0:1} != '#' -a ${string} != '\n' ] 
	then
		sudo sed -i "$num,$num2 s/^/#/g" $fileName
	fi
}

uncomment()
{
	#finding the pattern in server file
	fileName=$server_def
	line=`cat "$fileName" | grep -Fn "$1"`

	#checking if the pattern is in server file
	if [ -z $line ]
	then
		#finding the pattern in server file
		fileName=$client_def
		line=`cat "$client_def" | grep -Fn "$1"`
	fi
	
	#extracting the line num and the pattern of the test
	num=`echo "$line" | awk -F : '{ print $1 }'`
	string=`echo "$line" | awk -F : '{ print $2 }'`
	echo $string
	num2=$(($num+3))

    if [ ${string:0:1} == '#' -a ${string} != '\n' ]
	then
		echo "IM GOING TO UNCOMMENT"
		sudo sed -i "$num,$num2 s/#//g" $fileName
	fi
}


ini_get () {
    awk -v section="$2" -v variable="$3" '
        $0 == "[" section "]" { in_section = 1; next }
        in_section && $1 == variable {
            $1=""
            $2=""
            sub(/^[[:space:]]+/, "")
            print
            exit 
        }
        in_section && $1 == "" {
            # we are at a blank line without finding the var in the section
            print "Encounted a blank field in automation.cfg" > "/dev/stderr"
            exit 1
        }
    ' "$1"
}

option=$( ini_get automation.cfg HOST OPTION )
client_ip=$( ini_get automation.cfg CLIENT ip )
server_ip=$( ini_get automation.cfg SERVER ip )
host_ip=$( ini_get automation.cfg HOST ip)
client_passwd=$( ini_get automation.cfg CLIENT password )
server_passwd=$( ini_get automation.cfg SERVER password )
host_passwd=$( ini_get automation.cfg HOST password )
client_user=$( ini_get automation.cfg CLIENT user )
server_user=$( ini_get automation.cfg  SERVER user )
host_user=$( ini_get automation.cfg  HOST user ) 

# read the options
TEMP=`getopt -o o:dDcCh --long caliper_option:,check,dontcheck,copy,dontcopy,help -n 'main.sh' -- "$@"`
if [ $? -ne 0 ]
then
	cat help.txt
	exit
fi
#TEMP="$(getopt -o o:dDcCh --long caliper_option:,check,dontcheck,copy,dontcopy,help "./main.sh" -- "$@")"

eval set -- "$TEMP"

check=1
copy=0
# extract options and their arguments into variables.
while true ; do
    case "$1" in
        -o|--caliper_option)
	      caliper_option=$2
              lineNum=`cat $automationFile | grep "caliper_option" `	
	      sed -i "s/$lineNum/caliper_option\ =\ $caliper_option/g" $automationFile
	      shift 2 ;;
        -d|--check)
              check=1 ; shift;;
	-D|--dontcheck)
	      check=0 ; shift;;
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

caliper_option=$( ini_get automation.cfg EXECUTION_OPTION caliper_option )
echo -e "option=$option \n server_user=$server_user\n server_ip=$server_ip\n server_passwd=$server_passwd\n client_user=$client_user\n client_ip=$client_ip\n client_passwd=$client_passwd\n caliper_option=$caliper_option\n check = $check\n"
#Passing the read name as the parameter to the replace.sh
#sudo ./modify.py $path_config $client_ip $server_ip
/usr/bin/expect <<EOD
	spawn sudo ./modify.py $path_config $client_ip $server_ip
	expect {
		"assword" { send "$host_passwd\r"; exp_continue }
		eof { send_user "ConFig file has been modified\n\n" }
	}
EOD

#checking all the test to be conducted
while read testline
do
	if [ ${testline:0:1} != '#' -a -n $testline ]
	then
		uncomment $testline
	elif [ ${testline:0:1} == '#' ]
	then
		comment ${testline:1}
	fi
done<$testFile

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
	echo $target_arch
	if [ $target_arch == 'aarch64' ]
	then 
		if [ ! -d "./toolchain/gcc-linaro-aarch64-linux-gnu-4.9-2014.09_linux" ]
		then
			if [ -d toolchain ]
			then
				mkdir toolchain
			fi
			if [ -f "gcc-linaro-aarch64-linux-gnu-4.9-2014.09_linux.tar.bz2" ]
			then
				tar -xvf gcc-linaro-aarch64-linux-gnu-4.9-2014.09_linux.tar.bz2 &
				wait
				mv gcc-linaro-aarch64-linux-gnu-4.9-2014.09_linux ./toolchain
			else
				echo "The toolchain is not present "
				echo "Do you want me to download it for you [y/n]"
				if [ $option == "-f" ]
				then
					choice="y"
				else
					read choice
				fi
				if [ $choice == 'y' ]
				then
					wget https://releases.linaro.org/14.09/components/toolchain/binaries/gcc-linaro-aarch64-linux-gnu-4.9-2014.09_linux.tar.bz2 &
					wait
					tar -xvf gcc-linaro-aarch64-linux-gnu-4.9-2014.09_linux.tar.bz2 
					wait
					mv gcc-linaro-aarch64-linux-gnu-4.9-2014.09_linux ./toolchain
				else
					echo "Please download toolchain and then try again"
					exit 1
				fi
			fi
		fi
		files_toolchain="toolchain/gcc-linaro-aarch64-linux-gnu-4.9-2014.09_linux/bin"
	elif [ $target_arch == 'arm_32' ]
	then
		if [ ! -d "./toolchain/gcc-linaro-arm-linux-gnueabihf-4.9-2014.09_linux" ]
		then 
			if [ -d "toolchain" ]
			then
				mkdir toolchain
			fi
			if [ -f "gcc-linaro-arm-linux-gnueabihf-4.9-2014.09_linux.tar.bz2" ]
			then
				tar -xvf gcc-linaro-arm-linux-gnueabihf-4.9-2014.09_linux.tar.bz2 &
				wait
				mv gcc-linaro-arm-linux-gnueabihf-4.9-2014.09_linux ./toolchain
			else
			    echo "The toolchain is not present "
				echo "Do you want me to download it for you [y/n]"
				if [ $option == "-f" ]
				then
					choice="y"
				else
					read choice
				fi
				if [ $choice == 'y' ]
				then
					wget https://releases.linaro.org/14.09/components/toolchain/binaries/gcc-linaro-arm-linux-gnueabihf-4.9-2014.09_linux.tar.bz2 &
					wait
					tar -xvf gcc-linaro-arm-linux-gnueabihf-4.9-2014.09_linux.tar.bz2 &
					wait
					mv gcc-linaro-arm-linux-gnueabihf-4.9-2014.09_linux ./toolchain
				else
					echo "Please download toolchain and then try again"
					exit 1
				fi
			fi
		fi
		files_toolchain="toolchain/gcc-linaro-arm-linux-gnueabihf-4.9-2014.09_linux/bin"
	fi
   	export PATH=$PWD/$files_toolchain:$PATH
	if [ $? -ne 0 ]
	then 
		echo "Exporting the tool chain failed"
		exit
	fi
	echo "exporting $files_toolchain done"
fi


if [ $check == 1 ]
then
	sudo ./server_dependency.exp "$option" "$server_user" "$server_ip" "$server_passwd"
	if [ $? -eq 0 ]
	then
		echo "                      SERVER SUCESSFULL                                  "
	else
		echo "                      SERVER FAILED                                      "
	fi
	
	sudo ./host_dependency.exp "$option" 
	if [ $? -eq 0 ]
	then
		echo "                      HOST SUCESSFULL                                  "
	else
		echo "                      HOST FAILED                                      "
	fi

	sudo ./target_dependency.exp "$option" "$client_user" "$client_ip" "$client_passwd" 
fi

if [ $? -eq 0 ]
then
	echo -e "\n*********************************   Caliper is excuting   ***********************************\n"
	caliper $caliper_option  
	wait	
	echo -e "\n ********************************** caliper completed *****************************************\n"
        exit 0
else
	echo "Failed in Depenency"
    exit 1
fi

if [ $copy -eq 1 ]
then
	./copy.sh
fi
