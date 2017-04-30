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
	echo "usage: ./test_local_bw.sh <number_of_cores>. number of cores should be 1, 4, 16, 32 or 64"
	exit 1
fi

echo "\"read===="
echo "Command : taskset -c $taskset_core ./bw_mem -P $core -N 5 32M rd"
taskset -c $taskset_core ./bw_mem -P $core -N 5 32M rd
wait

echo "\"fread===="
echo "Command : taskset -c $taskset_core ./bw_mem -P $core -N 5 32M frd"
taskset -c $taskset_core ./bw_mem -P $core -N 5 32M frd
wait

echo "\"write===="
echo "Command : taskset -c $taskset_core ./bw_mem -P $core -N 5 32M wr"
taskset -c $taskset_core ./bw_mem -P $core -N 5 32M wr
wait

echo "\"fwrite===="
echo "Command : taskset -c $taskset_core ./bw_mem -P $core -N 5 32M fwr"
taskset -c $taskset_core ./bw_mem -P $core -N 5 32M fwr
wait

echo "\"bzero===="
echo "Command : taskset -c $taskset_core ./bw_mem -P $core -N 5 32M bzero"
taskset -c $taskset_core ./bw_mem -P $core -N 5 32M bzero
wait

echo "\"readwrite===="
echo "Command : taskset -c $taskset_core ./bw_mem -P $core -N 5 32M rdwr"
taskset -c $taskset_core ./bw_mem -P $core -N 5 32M rdwr
wait

echo "\"copy===="
echo "Command : taskset -c $taskset_core ./bw_mem -P $core -N 5 32M cp"
taskset -c $taskset_core ./bw_mem -P $core -N 5 32M cp
wait

echo "\"fcopy===="
echo "Command : taskset -c $taskset_core ./bw_mem -P $core -N 5 32M fcp"
taskset -c $taskset_core ./bw_mem -P $core -N 5 32M fcp
wait

echo "\"bcopy===="
echo "Command : taskset -c $taskset_core ./bw_mem -P $core -N 5 32M bcopy"
taskset -c $taskset_core ./bw_mem -P $core -N 5 32M bcopy
wait
