#!/bin/bash

if [ $# -lt 5 ]; then
    echo "Usage: ~/caliper_redis/redis_benchmark.sh <type of test: SHORT | BASIC | PIPELINE> <ip address> <start cpu number> <redis instance number> <keep alive count> <pipeline> <data number> <data size> <key space length>"
    exit 1
fi

ip_addr=${2}
base_port_num=7000
start_cpu_num=${3}
redis_inst_num=${4}
keep_alive=${5}
pipeline=${6}
data_num=${7}
data_size=${8}
key_space_len=${9}

service irqbalance stop

echo 1 > /proc/sys/net/ipv4/tcp_timestamps
echo 1 > /proc/sys/net/ipv4/tcp_tw_reuse
echo 1 > /proc/sys/net/ipv4/tcp_tw_recycle
echo 2048 65000 > /proc/sys/net/ipv4/ip_local_port_range
echo 2621440 > /proc/sys/net/core/somaxconn
echo 2621440 > /proc/sys/net/core/netdev_max_backlog
echo 2621440 > /proc/sys/net/ipv4/tcp_max_syn_backlog
echo 1 > /proc/sys/net/netfilter/nf_conntrack_tcp_timeout_time_wait
echo 2621440 > /proc/sys/net/netfilter/nf_conntrack_max
ulimit -n 1024000

python ./generate_inputdata.py ./input_data ${data_num} ${data_size}

let "redis_inst_num--"

for index in $(seq 0 ${redis_inst_num})
do
    echo "call redis-cli to initialize data for redis-${index}"
    port=`expr ${base_port_num} + ${index} + ${start_cpu_num}`
    echo "flushdb" | ./redis-cli -h ${ip_addr} -p ${port} --pipe
    cat ./input_data | ./redis-cli -h ${ip_addr} -p ${port} --pipe

/usr/bin/expect <<EOF
set timeout 40
spawn ./redis-cli -h ${ip_addr} -p ${port}
expect "${ip_addr}:${port}>"
send "config set stop-writes-on-bgsave-error no\r"
expect "OK"
expect "${ip_addr}:${port}>"
send "quit\r"
expect eof
EOF

done

for index in $(seq 0 ${redis_inst_num})
do
    port=`expr ${base_port_num} + ${index} + ${start_cpu_num}`
    taskindex=${index}
    echo "call redis-benchmark to test redis-${index}"
    taskset -c ${taskindex} ./redis-benchmark -h ${ip_addr} -p ${port} -c 50 -n ${data_num} -d ${data_size} -k ${keep_alive} -r ${key_space_len} -P ${pipeline} -t get $1
done
