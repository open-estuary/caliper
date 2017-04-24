#!/bin/bash

#####################
#args modify
max_requests="30000"
test_name="cpu"
cpu_max_prime="100000"
num_threads=$(grep 'processor' /proc/cpuinfo |sort |uniq |wc -l)

if [ $max_requests -eq 0 ]; then 
    max_requests=100000
fi

sysbench_dir=sysbench-0.5
if [ ! -d $sysbench_dir ]; then
    printf "%s[%3d]%5s: sysbench not ready, need run sysbench.sh first\n" "${FUNCNAME[0]}" ${LINENO} "Error"
    exit 1
fi

#####################
#mysql env ready
sMysqlInfo=$(whereis mysql |cut -d: -f2-)
if [ -z "${sMysqlInfo}" ]; then
    printf "%s[%3d]%5s: mysql not found\n" "${FUNCNAME[0]}" ${LINENO} "Error"
    exit 1
fi

#mysql lib
s1=$(find ${sMysqlInfo} -name "libmysqlclient.so" 2>/dev/null)
if [ -n "${s1}" ]; then
    s2=$(sed -n "1p" <<< "${s1}")
    drLibMysql=$(dirname "${s2}")
fi
if [ ! -d "${drLibMysql}" ]; then
    printf "%s[%3d]%5s: mysql lib not found\n" "${FUNCNAME[0]}" ${LINENO} "Error"
    exit 1
fi
dr1=$(sed "s/\./\\\./g" <<< "${drLibMysql}")
grep -q "\(^\|:\)${dr1}\(:\|$\)" <<< "${LD_LIBRARY_PATH}"
if [ $? -ne 0 ]; then
    export LD_LIBRARY_PATH=${drLibMysql}:${LD_LIBRARY_PATH}
fi

#####################
#sysbench run
$sysbench_dir/sysbench/sysbench \
    --num-threads=$num_threads \
    --max-requests=$max_requests \
    --test=$test_name \
    --cpu-max-prime=$cpu_max_prime \
    run

if [ $? -ne 0 ]; then
    printf "%s[%3d]%5s: test cpu num_threads[${num_threads}] failed\n" "${FUNCNAME[0]}" ${LINENO} "Error"
    exit 1
fi

num_threads=1
$sysbench_dir/sysbench/sysbench \
    --num-threads=$num_threads \
    --max-requests=$max_requests \
    --test=$test_name \
    --cpu-max-prime=$cpu_max_prime \
    run

if [ $? -ne 0 ]; then
    printf "%s[%3d]%5s: test cpu num_threads[${num_threads}] failed\n" "${FUNCNAME[0]}" ${LINENO} "Error"
    exit 1
fi

