#!/bin/bash

CC=gcc
CFLAGS+=i-Icommon_32bit -lrt -lm
all: dhry1 dhry2 whets lloops lpack

clean:
	rm -fr dhry1 dhry2 whets lloops lpack
	-rm -fr *.txt

dhry1: dhrystone1/dhry1.c common_32bit/cpuidc.c
	$(CC) $^ $(CFLAGS) -o $@

dhry2: dhrystone2/dhry_1.c dhrystone2/dhry_2.c common_32bit/cpuidc.c 
	$(CC) $^ $(CFLAGS) -o $@

whets: whetstone/whets.c common_32bit/cpuidc.c
	$(CC) $^ $(CFLAGS) -o $@

lloops: livermore_loops/lloops.c common_32bit/cpuidc.c
	$(CC) $^ $(CFLAGS) -o $@

lpack: linpack/linpack.c common_32bit/cpuidc.c
	$(CC) $^ $(CFLAGS) -o $@


    
