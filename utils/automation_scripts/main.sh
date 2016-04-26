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

	if [ ${string:0:1} != '#' ]
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
	num2=$(($num+3))

	if [ ${string:0:1} == '#' ]
	then
		sudo sed -i "$num,$num2 s/#//g" $fileName
	fi
}

echo -e "option=$option \n server_id=$server_id\n server_ip=$server_ip\n server_passwd=$server_passwd\n client_id=$client_id\n client_ip=$client_ip\n client_passwd=$client_passwd\n caliper_option=$caliper_option\n"
 
#Passing the read name as the parameter to the replace.sh
path_config="/etc/caliper/config/client_config.cfg"
sudo ./modify.py $path_config $client_ip $server_ip

host_arch=`uname -a | awk -F ' ' '{print $12}'`
target_arch=`ssh $client_id@$client_ip "uname -a"`
target_arch=`echo $target_arch | awk -F ' ' '{print $13}'`
if [ $host_arch != $target_arch ]
then
    toolchain_flag=0
    #Exporting the Tool chain
    files_toolchain=`find ~/toolchain/ -mindepth 1 -maxdepth 1 -type d -printf "%f\n"`
    for i in $files_toolchain
    do
        toolchain_flag=$(($toolchain_flag + 1))
        export PATH=~/toolchain/$i/bin:$PATH
    done

    if [ $toolchain_flag -eq 0 ]
    then
        echo -e "\nThe Toolchain Path is invalid\n"
        exit
    elif [ $toolchain_flag -eq 1 ]
    then
        echo -e "\n ONLY $i toolchain is exported\n"
        echo "This will lead to error Please"
        sleep 5
    fi
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


sudo ./target_dependency.exp "$option" "$client_id" "$client_ip" "$client_passwd" "$toolchain"
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

