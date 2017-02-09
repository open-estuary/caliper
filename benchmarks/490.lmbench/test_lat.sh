#!/bin/bash
#SPV
var_P=$1
physcpubind=""
membind=$2

if [ $membind -eq 0 ];
then
	echo "Local memory access:"
elif [ $membind -eq 1 ]
then
	echo "Cross memory access:"
else
	echo " Error in passing memorybind value"	
	exit 1
fi

if [ $var_P -eq 1 ];
then
	physcpubind="0"
elif [ $var_P -eq 4 ];
then
	physcpubind="0-3"
elif [ $var_P -eq 16 ];
then
	physcpubind="0-15"
elif [ $var_P -eq 32 ];
then
	physcpubind="0-31"
else
	echo "usage: ./test_local_lat.sh <number_of_threads number of threads should be 1, 4, 16, 32 > <membinding 0,1>"
	exit 1
fi

echo "numactl --membind=$membind --physcpubind=$physcpubind ./lat_mem_rd -P $var_P -t 32M 128"
numactl --membind=$membind --physcpubind=$physcpubind ./lat_mem_rd -P $var_P -t 32M 128
wait

