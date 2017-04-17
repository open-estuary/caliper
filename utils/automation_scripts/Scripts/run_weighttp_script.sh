#!/bin/bash

if [ "$#" -ne 7 ]; then
        echo "Usage: <script_name> <user name of target platform> <ip address of target platform eth interface> <port number> <no_of_cpus> <start_cpu> <number of requests> <html filename>"
        exit 1
fi

username=$1
ip_address=$2
port_number=$3
cpu_count=$4
cpu_start_no=$5
no_requests=$6
html_filename=$7

e=$(( $cpu_start_no + (( $cpu_count - 1 )) ))
cpu_range="$cpu_start_no-$e"

while [ 1 ];
do
	process=`ssh $username@$ip_address ps -ef | grep -c "nginx: worker process"`
	if [ $process -gt 1 ]; then 
		taskset -c $cpu_range weighttp -n $no_requests -c 512 -k -t 24 http://$ip_address:$port_number/$html_filename
		break
	fi 
	sleep 1
done
