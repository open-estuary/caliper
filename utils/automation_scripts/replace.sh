#!/bin/bash 

#Parameters to be changed according to the host machine
path="/etc/caliper/config"
client_config="$path/client_config.cfg"
flag=0

#checking if the CLA have been passed
if [ $# > 1 ]
then
	#file descriptor for the client_config.cgf file.
	exec 3< $client_config

	#seeking to the line which contains [client]
	while [ $flag -eq 0 ]
	do
 		#Reading the file line by line.
		read line <&3

		#checking if the read string length is > 0
		if [ -n $line ]
		then
			#checking if the read string is == [client]
			if [ $line = '[CLIENT]' ]
			then
				flag=1
			fi	
		fi
	done
	flag=0;

	#navigate to the next non commentable line
	while [ $flag -eq 0 ]
	do	
 		#Reading the file line by line.
		read line <&3
		if [ ${line[0]:0:1} != '#' ]
		then
			flag=1
		fi
	done

	#close all the file descripter
	exec 3>&- 
	
	#extracting the ip address
	ip=`echo "$line" | awk -F : ' { print $2 }' `

	#inplace replacement of the txt
	sudo sed -i "s/$ip/$1/g" $client_config
else
	echo "Missing CLA"
	echo "enter the ip address in the folling format"
	echo "./replace 192.168.40.X"
fi
clear
sudo cat $client_config
sleep 5
clear
