#!/bin/bash

ip_address=$1
port_number=$2
no_requests=$3
html_filename=$4

COUNTER=0
while [ 1 ];
do
	process=`ssh root@$ip_address ps -ef | grep nginx | wc -l`
	if [ $process -gt 1 ]; then 
		weighttp -n $no_requests -c 512 -k -t 24 http://$ip_address:$port_number/$html_filename
		break
	fi 
	sleep 1
	let COUNTER=COUNTER+1
done
