#!/bin/bash

TOPDIR=${0%/*}
cd $TOPDIR

if [ $# -lt 3 ]; then
    echo "Usage: client_start.sh {init | test}  <ip_address> <start_cpu_number> <redis_inst_number> <keep_alive> <pipe_num>"
    exit 0
fi


REDIS_TEST_DIR=/tmp/redis

#######################################################################################
# Notes:
#  To start client tests
#  Usage: client_start.sh {init | test} <ip_addr> <start_cpu_num> <redis_inst> <keep-alive> <pipe_num>
#######################################################################################

ip_addr=$2
base_port_num=7000
start_cpu_num=$3
redis_inst_num=$4
keep_alive=$5
pipeline=$6

data_num=10000000
data_size=10
key_space_len=10000

if [[ ${pipeline} -eq 100 ]] ; then
    echo "Change num_of_req to 100000000"
    data_num=100000000
fi
    
if [ "$1" == "init" ] ; then
    echo "init"
    #Step 1: Prepare data
    mkdir -p ${REDIS_TEST_DIR}

    echo 1 > /proc/sys/net/ipv4/tcp_timestamps
    echo 1 > /proc/sys/net/ipv4/tcp_tw_reuse
    echo 1 > /proc/sys/net/ipv4/tcp_tw_recycle
    echo 2048 65000 > /proc/sys/net/ipv4/ip_local_port_range
    echo 2621440 > /proc/sys/net/core/somaxconn
    echo 2621440 > /proc/sys/net/core/netdev_max_backlog
    echo 2621440 > /proc/sys/net/ipv4/tcp_max_syn_backlog

    ulimit -n 1024000
    #data_num=10000
    #data_size=128

    python generate_inputdata.py ${REDIS_TEST_DIR}/input_data ${data_num} ${data_size}
   
# redis_inst_num=`expr $redis_inst_num - 1`
    let "redis_inst_num--"
    for index in $(seq 0 ${redis_inst_num})
    do
        echo "call redis-cli to initialize data for redis-${index}"
        port=`expr ${base_port_num} + ${index} + ${start_cpu_num}`
        echo "flushdb"  |  redis-cli -h ${ip_addr} -p ${port} --pipe
        cat $REDIS_TEST_DIR/input_data | redis-cli -h ${ip_addr} -p ${port} --pipe
    done

elif [ "$1" == "test" ] ; then
    rm ${REDIS_TEST_DIR}/redis_benchmark_log*

#    redis_inst_num=`expr $redis_inst_num - 1`
    let "redis_inst_num--"
    for index in $(seq 0 ${redis_inst_num})
    do
        port=`expr ${base_port_num} + ${index} + ${start_cpu_num}`
        taskindex=`expr 1 + ${index}`
        #taskend=`expr 6 + ${taskindex}`
        echo "call redis-benchmark to test redis-${index}"
        
        #if testing perfrmance of twemproxy+redis cluster,you should uncomment next line#
        #port=22121

        taskset -c ${taskindex} redis-benchmark -h ${ip_addr} -p ${port} -c 50 -n ${data_num} -d ${data_size} -k ${keep_alive} -r ${key_space_len} -P ${pipeline} -t get > ${REDIS_TEST_DIR}/redis_benchmark_log_${port} & 
        #${REDIS_CMD_DIR}/redis-benchmark -h ${ip_addr} -p ${port} -c 50 -n ${data_num} -d ${data_size} -k ${keep_alive} -r ${key_space_len} -P ${pipeline} -t get > redis_benchmark_log_${port} &
    done

    echo "Please check results under ${REDIS_TEST_DIR} directory"
    echo "You could use scripts/analysis_qps_lat.py to get qps and latency from logs"

else 
    echo "parameter should be {init | test} "
fi

echo "**********************************************************************************"

