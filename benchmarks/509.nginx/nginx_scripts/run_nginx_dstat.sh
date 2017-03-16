#!/bin/bash

#set -x

if [ "$#" -lt 5 ]; then
	echo "Usage: <script_name> <number of clients> <ip address for 1st client> <no_of_cpus> <start_cpu>"
	exit 1
fi

valid_arg_count=$(( (( (( (($1 - 1 )) )) * 4 )) + 5 ))
if [ "$#" -ne $valid_arg_count ]; then
        echo "Usage: <script_name> <number of clients> <ip address for 1st client> <no_of_cpus> <start_cpu>"
        exit 1
fi

NO_OF_CLIENTS=$1

flag=0
COUNTER=0

declare -a client_status
declare -a weighttp_status
declare -a client_port
declare -a client_ip
declare -a cpu_range

for (( i=0; i<$NO_OF_CLIENTS; i++ ))
do
	client_status[$i]=0
	port=$(( 3 + (( $i * 4 )) ))
	client_port[$i]=${!port}
	ip=$(( 2 + (( $i * 4 )) ))
	client_ip[$i]=${!ip}

	yes | cp ../nginx_config_files/conf/my_nginx.conf /usr/local/nginx/conf/my_nginx.conf$i
	sed -ie "s/index.html/index$i.html/g" /usr/local/nginx/conf/my_nginx.conf$i

	str=${client_ip[$i]}
	str1=${client_port[$i]}

	sed -ie "s/ip_port/$str:$str1/g" /usr/local/nginx/conf/my_nginx.conf$i
	if [ ! -f /usr/local/nginx/html/index$i.html ]; then
		cp /usr/local/nginx/html/index.html /usr/local/nginx/html/index$i.html
	fi

	s=$(( 5 + (( $i * 4 )) ))
	t=$(( 4 + (( $i * 4 )) ))
	e=$(( ${!s} + (( ${!t} - 1 )) ))
	cpu_range[$i]=${!s}-$e

	taskset -c ${cpu_range[$i]} ../nginx -c /usr/local/nginx/conf/my_nginx.conf$i
done

COUNTER=0
while [ $COUNTER -lt 2000 ]; 
do
	for (( i=0; i<$NO_OF_CLIENTS; i++ ))
	do
		weighttp_status[$i]=`netstat -ant | grep "${client_port[$i]}" | awk 'END {print}' | awk '{print $6}'`
		if [ "${weighttp_status[$i]}" == "LISTEN" -a $flag -eq 0 ]; then
			#echo "client $i is in listening mode"
			client_status[$i]=1
		fi

		if [ \( "${weighttp_status[$i]}" == "ESTABLISHED" -o "${weighttp_status[$i]}" == "TIME_WAIT" \) -a ${client_status[$i]} -eq 1 ]; then
			echo "client $i is started weighttp process"
			client_status[$i]=2
		fi
	done

	for (( i=0; i<$NO_OF_CLIENTS; i++ ))
	do
		if [ "${client_status[$i]}" == "2" ]; then
			continue			
		else
			break
		fi
	done

	if [ $i -eq $NO_OF_CLIENTS ]; then
		echo "all clients has established the connection to server"
		break		
	fi 

	sleep 0.2
	let COUNTER=COUNTER+1
done

if [ $COUNTER -eq 2000 ]; then
	echo "one or more clients has not able to establish the connection to nginx server"
	killall nginx
	exit 1
fi

dstat &	

COUNTER=0

while [ $COUNTER -lt 4000 ];
do
	for (( i=0; i<$NO_OF_CLIENTS; i++ ))
	do
		weighttp_status[$i]=`netstat -ant | grep "${client_port[$i]}" | awk 'END {print}' | awk '{print $6}'`
		if [ "${weighttp_status[$i]}" == "LISTEN" ]; then
			echo "client $i weighttp process is completed"
			client_status[$i]=3
		fi
	done

	for (( i=0; i<$NO_OF_CLIENTS; i++ ))
	do
		if [ "${client_status[$i]}" == "3" ]; then
			continue
		else
			break
		fi
	done

	if [ $i -eq $NO_OF_CLIENTS ]; then
		echo "all clients has completed weighttp process"
		killall dstat
		killall nginx
		break		
	fi 

	sleep 1 
done

if [ $COUNTER -eq 4000 ]; then
	echo "one or more clients has not been completed the weighttp process"
	killall dstat
	killall nginx
	exit 1
fi


