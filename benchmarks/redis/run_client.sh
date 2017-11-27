#!/bin/bash

#Define global APP_ROOT directory

TOPDIR=${0%/*}
cd $TOPDIR

if [ -z "${1}" ] ; then
    echo "Usage: ./run_test.sh <server ip>"
    exit 0
fi

ip="${1}"


#APP_CUR_DIR=$(cd `dirname $0` ; pwd)
#APP_ROOT_DIR=$(cd `dirname $0` ; cd ../../../; pwd)

echo "Try to connect server-${ip}......"


#echo "Disable unused CPU..."
#${APP_CUR_DIR}/scripts/enable_cpus.sh 32 64 0

test_log_dir="/tmp/redis/"
mkdir $test_log_dir

check_redis_benchmark() {
    while [[ 1 ]]
    do
        is_running=$(ps -aux | grep redis-benchmark | grep -v grep)
        if [ -z "${is_running}" ] ; then
            return 
        else
            echo "Wait for redis-benchmark done......"
            sleep 60
        fi
    done
} 

max_inst=3
cur_inst=1

while [ ${cur_inst} -lt ${max_inst} ] ; 
do

start_cpu_num=1
inst_num=${cur_inst}
echo "Initialize database......"
scripts/init_test.sh init ${ip} ${start_cpu_num} ${inst_num} 
#mkdir -p log/${cur_inst}/

echo "Short case" 
scripts/init_test.sh test ${ip} ${start_cpu_num} ${inst_num} 0 1
check_redis_benchmark 
#scripts/analysis_qps_lat.py ${test_log_dir} ${inst_num} >> redis_log_${cur_inst}
scripts/analysis_qps_lat.py ${test_log_dir} ${inst_num} >> /tmp/redis_output.log

#mkdir -p log/${cur_inst}/short
#mv ${test_log_dir}/redis_benchmark_log* log/${cur_inst}/short

echo "Basic case"
scripts/init_test.sh test ${ip} ${start_cpu_num} ${inst_num} 1 1
check_redis_benchmark
#scripts/analysis_qps_lat.py ${test_log_dir} ${inst_num} >> redis_log_${cur_inst}
scripts/analysis_qps_lat.py ${test_log_dir} ${inst_num} >> /tmp/redis_output.log

#mkdir -p log/${cur_inst}/basic
#mv ${test_log_dir}/redis_benchmark_log* log/${cur_inst}/basic

echo "Pipeline case"
scripts/init_test.sh test ${ip} ${start_cpu_num} ${inst_num} 1 100
check_redis_benchmark
#scripts/analysis_qps_lat.py ${test_log_dir} ${inst_num} >> redis_log_${cur_inst}
scripts/analysis_qps_lat.py ${test_log_dir} ${inst_num} >> /tmp/redis_output.log

#mkdir -p log/${cur_inst}/pipeline
#mv ${test_log_dir}/redis_benchmark_log* log/${cur_inst}/pipeline

let "cur_inst++"

done

echo "Enable unused CPU after test ..."
#${APP_CUR_DIR}/scripts/enable_cpus.sh 32 64 1
