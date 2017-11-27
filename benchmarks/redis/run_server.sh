#!/bin/bash

TOPDIR=${0%/*}
cd $TOPDIR

#Start 
start_cpu_num=1
inst_num=2
end_cpu_num=$[$start_cpu_num+$inst_num-1]

scripts/start_server.sh $start_cpu_num $end_cpu_num
