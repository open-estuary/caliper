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
elif [ $core -eq 32 ];
then
	taskset_core="0-31"
elif [ $core -eq 64 ];
then
	taskset_core="0-31,32-63"
else
	echo "usage:usage: ./test_local_bw.sh <number_of_cores>. number of cores should be 1, 4, 16, 32 or 64"
	exit 1
fi

echo "\"read===="
taskset -c $taskset_core ./bw_mem -P $core -N 5 32M rd
wait

echo "\"fread===="
taskset -c $taskset_core ./bw_mem -P $core -N 5 32M frd
wait

echo "\"write===="
taskset -c $taskset_core ./bw_mem -P $core -N 5 32M wr
wait

echo "\"fwrite===="
taskset -c $taskset_core ./bw_mem -P $core -N 5 32M fwr
wait

echo "\"bzero===="
taskset -c $taskset_core ./bw_mem -P $core -N 5 32M bzero
wait

echo "\"readwrite===="
taskset -c $taskset_core ./bw_mem -P $core -N 5 32M rdwr
wait

echo "\"copy===="
taskset -c $taskset_core ./bw_mem -P $core -N 5 32M cp
wait

echo "\"fcopy===="
taskset -c $taskset_core ./bw_mem -P $core -N 5 32M fcp
wait

echo "\"bcopy===="
taskset -c $taskset_core ./bw_mem -P $core -N 5 32M bcopy
wait
