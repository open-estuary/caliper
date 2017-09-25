#!/bin/bash
sysbench_dir=sysbench-0.5
num_threads1="1"
max_requests="30000"
test_name="cpu"
cpu_max_prime="100000"
num_threads=$(grep 'processor' /proc/cpuinfo |sort |uniq |wc -l)
#test_name="$PWD/sysbench-0.5/sysbench/tests/cpu"
if [ ! -d $sysbench_dir ]; then
  bzr branch lp:~sysbench-developers/sysbench/0.5 $sysbench_dir
  if [ $? -ne 0 ]; then
    echo 'Download the sysbench failed'
    exit 1
  fi
fi

if [ ! -d $sysbench_dir ]; then
    echo 'sysbench has not been download completely'
    exit 1
fi

export PATH=$PATH:/usr/local

pushd $sysbench_dir
  ./autogen.sh
  ./configure 
  make -s 
  make install
popd
if [ $max_requests -eq 0 ]; then 
    max_requests=100000
fi
set -x

 $sysbench_dir/sysbench/sysbench \
  --num-threads=$num_threads \
  --max-requests=$max_requests \
  --test=$test_name \
  --cpu-max-prime=$cpu_max_prime \
  run

 $sysbench_dir/sysbench/sysbench \
  --num-threads=1 \
  --max-requests=$max_requests \
  --test=$test_name \
  --cpu-max-prime=$cpu_max_prime \
  run
if [ $? -ne 0 ]; then
    echo 'Run the cpu test failed'
    exit 1
fi


