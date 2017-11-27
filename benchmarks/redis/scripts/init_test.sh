#!/bin/bash

TOPDIR=${0%/*}
cd $TOPDIR

echo "Try to connect server-${ip}......"

if [ $# -lt 2 ] ; then 
    echo "Usage: ./init_test.sh {init | test} ${ip} {start_cpu_num} {redis-inst:1 ~ 32} {keep-alive:0 or 1} {pipeline:0 ~ 100}"
    exit 0
fi

#Include common setup utility functions
./start_client.sh $@


