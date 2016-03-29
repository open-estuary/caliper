#!/bin/bash
################################################################################
##                                                                            ##
## Copyright (c) International Business Machines  Corp., 2008                 ##
##                                                                            ##
## This program is free software;  you can redistribute it and#or modify      ##
## it under the terms of the GNU General Public License as published by       ##
## the Free Software Foundation; either version 2 of the License, or          ##
## (at your option) any later version.                                        ##
##                                                                            ##
## This program is distributed in the hope that it will be useful, but        ##
## WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY ##
## or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License   ##
## for more details.                                                          ##
##                                                                            ##
## You should have received a copy of the GNU General Public License          ##
## along with this program;  if not, write to the Free Software               ##
## Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA    ##
##                                                                            ##
## Author:      Veerendra <veeren@linux.vnet.ibm.com>

# This script is trying to ping the Child2 from Child1
# The test case ID, the test case count and the total number of test case

TCID=${TCID:-netns_child_1.sh}
TST_TOTAL=1
TST_COUNT=1
export TCID
export TST_COUNT
export TST_TOTAL

. netns_initialize.sh
status=0

    # Writing child PID number into /tmp/FIFO
    tst_timeout "echo $$ > /tmp/FIFO2" $NETNS_TIMEOUT
    if [ $? -ne 0 ]; then
        tst_brkm TBROK "timeout reached!"
    fi

    # Reading device name from parent
    vnet1=$(tst_timeout "cat /tmp/FIFO1" $NETNS_TIMEOUT)
    if [ $? -ne 0 ]; then
        tst_brkm TBROK "timeout reached!"
    fi
    debug "INFO: CHILD1: Network dev name received $vnet1";

    # By now network is working
    ifconfig $vnet1 $IP2$mask up > /dev/null 2>&1
    ifconfig lo up

    # Creating ssh session
    /usr/sbin/sshd -p $PORT
    if [ $? ]; then
        debug "INFO: Started the sshd in CHILD1"
        sshpid1=`ps -ef | grep "sshd -p $PORT" | awk '{ print $2 ; exit 0} ' `

        ping -qc 2 $IP1 > /dev/null
        if [ $? -ne 0 ] ; then
            tst_resm TFAIL "FAIL: Unable to ping the Parent1 from Child1"
            status=-1
        fi
    else
        tst_resm TFAIL "FAIL: Unable to start sshd in child1"
        status=-1
    fi

    # Waiting for CHILD2
    ret=$(tst_timeout "cat /tmp/FIFO5" $NETNS_TIMEOUT)
    if [ $? -ne 0 ]; then
        tst_brkm TBROK "timeout reached!"
    fi

    if [ "$ret" = "0" ]; then
        # Pinging CHILD2 from CHILD1
        debug "INFO: Trying to ping CHILD2..."
        ping -qc 2 $IP4 > /dev/null
        if [ $? -eq 0 ];
        then
            tst_resm TINFO "PASS: Child2 is pinging from CHILD1 !"
        else
            tst_resm TFAIL "FAIL: Unable to Ping Child2 from CHILD1 !"
            status=-1
        fi
    else
        tst_resm TFAIL "CHILD2 is unable to reach CHILD1"
        status=-1
    fi
    cleanup $sshpid1 $vnet1
    debug "INFO: ********End of Child-1 $0********"
    exit $status
