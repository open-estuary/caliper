#!/bin/bash

core=$1
taskset_core=0 

if [ $core -eq 1 ];
then
	taskset_core="0"
elif [ $core -eq 4 ];
then
	taskset_core="0-3"
elif [ $core -eq 16 ];
then
	taskset_core="0-15"
else
	echo "usage: ./test_cross_bw.sh <number_of_cores>. number of cores should be 1, 4 or 16"
	exit 1
fi

echo "\"read===="
numactl -C $taskset_core -m 1 ./bw_mem -P $core -N 5 32M rd
wait

echo "\"fread===="
numactl -C $taskset_core -m 1 ./bw_mem -P $core -N 5 32M frd
wait

echo "\"write===="
numactl -C $taskset_core -m 1 ./bw_mem -P $core -N 5 32M wr
wait

echo "\"fwrite===="
numactl -C $taskset_core -m 1 ./bw_mem -P $core -N 5 32M fwr
wait

echo "\"bzero===="
numactl -C $taskset_core -m 1 ./bw_mem -P $core -N 5 32M bzero
wait

echo "\"readwrite===="
numactl -C $taskset_core -m 1 ./bw_mem -P $core -N 5 32M rdwr
wait

echo "\"copy===="
numactl -C $taskset_core -m 1 ./bw_mem -P $core -N 5 32M cp
wait

echo "\"fcopy===="
numactl -C $taskset_core -m 1 ./bw_mem -P $core -N 5 32M fcp
wait

echo "\"bcopy===="
numactl -C $taskset_core -m 1 ./bw_mem -P $core -N 5 32M bcopy
wait
