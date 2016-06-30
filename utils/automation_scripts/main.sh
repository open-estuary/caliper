#!/bin/bash
# -*- coding:utf-8 -*-
#
#   Author  :   Dikshit N
#   E-mail  :   dikshit.n@huawei.com
#   Date    :   22/04/16 
#
path="/etc/caliper/test_cases_cfg/"
ipFile="ipList"
testFile="testList"
server_def="$path/server_cases_def.cfg"
client_def="$path/common_cases_def.cfg"
clear
if [ $# -eq 8 ]
then
	option=$1
	server_id=$2
	server_ip=$3
	server_passwd=$4
	client_id=$5
	client_ip=$6
	client_passwd=$7
	caliper_option=$8
elif [ $# -eq 7 ]
then
	
	option=" "
	server_id=$1
	server_ip=$2
	server_passwd=$3
	client_id=$4
	client_ip=$5
	client_passwd=$6
	caliper_option=$7
fi

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

echo -e "option=$option \n server_id=$server_id\n server_ip=$server_ip\n server_passwd=$server_passwd\n client_id=$client_id\n client_ip=$client_ip\n client_passwd=$client_passwd\n caliper_option=$caliper_option\n"
 
#Passing the read name as the parameter to the replace.sh
path_config="/etc/caliper/config/client_config.cfg"
sudo ./modify.py $path_config $client_ip $server_ip


#Comparing the tool chain
target_arch=`ssh $client_id@$client_ip "uname -a"`
target_arch=`echo $target_arch | awk -F ' ' '{print $12}'`
host_arch=`uname -a |  awk -F ' ' '{print $12}'`


#Exporting the Tool chain
echo "Target arch = $target_arch"
echo "Host arch = $host_arch"
if [ $target_arch != $host_arch ]
then
	target_arch=`ssh $client_id@$client_ip "uname -a"`
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
				mv gcc-linaro-aarch64-linux-gnu-4.9-2014.09_linux ./toolchain/
			else
				echo "The toolchain is not present "
				echo "Do you want me to download it for you [y/n]"
				read choice
				if [ $choice == 'y' ]
				then
					wget https://releases.linaro.org/14.09/components/toolchain/binaries/gcc-linaro-aarch64-linux-gnu-4.9-2014.09_linux.tar.bz2 &
					wait
					tar -xvf gcc-linaro-aarch64-linux-gnu-4.9-2014.09_linux.tar.bz2 
					wait
					mv gcc-linaro-aarch64-linux-gnu-4.9-2014.09_linux ./toolchain/
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
				mv gcc-linaro-arm-linux-gnueabihf-4.9-2014.09_linux ./toolchain/
			else
			    echo "The toolchain is not present "
				echo "Do you want me to download it for you [y/n]"
				read choice
				if [ $choice == 'y' ]
				then
					wget https://releases.linaro.org/14.09/components/toolchain/binaries/gcc-linaro-arm-linux-gnueabihf-4.9-2014.09_linux.tar.bz2 &
					wait
					tar -xvf gcc-linaro-arm-linux-gnueabihf-4.9-2014.09_linux.tar.bz2 &
					wait
					mv gcc-linaro-arm-linux-gnueabihf-4.9-2014.09_linux ./toolchain/
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

sudo ./server_dependency.exp "$option" "$server_id" "$server_ip" "$server_passwd"
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


sudo ./target_dependency.exp "$option" "$client_id" "$client_ip" "$client_passwd" 
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

