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
## Author:      Veerendra <veeren@linux.vnet.ibm.com>                         ##
################################################################################

# The test case ID, the test case count and the total number of test case

TCID=${TCID:-netns_parent_2.sh}
TST_TOTAL=1
TST_COUNT=1
export TCID
export TST_COUNT
export TST_TOTAL
. netns_initialize.sh

    create_veth
    vnet2=$dev0
    vnet3=$dev1

    if [ -z "$vnet2" -o -z "$vnet3" ] ; then
        tst_resm TFAIL  "Error: unable to create veth pair in $0"
        exit 1
    else
        debug "INFO: vnet2 = $vnet2 , vnet3 = $vnet3"
    fi
    ifconfig $vnet2 $IP3$mask up > /dev/null 2>&1
    route add -host $IP4 dev $vnet2
    echo 1 > /proc/sys/net/ipv4/conf/$vnet2/proxy_arp

    pid=$(tst_timeout "cat /tmp/FIFO4" $NETNS_TIMEOUT)
    if [ $? -ne 0 ]; then
        tst_brkm TBROK "timeout reached!"
    fi
    debug "INFO: The pid of CHILD2 is $pid"
    ip link set $vnet3 netns $pid
    tst_timeout "echo $vnet3 > /tmp/FIFO3" $NETNS_TIMEOUT
    if [ $? -ne 0 ]; then
        tst_brkm TBROK "timeout reached!"
    fi

    debug "INFO: PARENT-2: End of $0"
    exit 0
