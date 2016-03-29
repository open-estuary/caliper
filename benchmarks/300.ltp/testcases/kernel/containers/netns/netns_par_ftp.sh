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

# This script checks whether child NS is reachable from parent NS.
#set -x

# The test case ID, the test case count and the total number of test case

TCID=${TCID:-par_ftp.sh}
TST_TOTAL=1
TST_COUNT=1
export TCID
export TST_COUNT
export TST_TOTAL

    ping -q -c 2 $IP2 > /dev/null

    if [ $? = 0 ] ; then
        tst_resm TINFO "Pinging ChildNS from ParentNS"
	status=0
    else
        tst_resm TFAIL "Error: Unable to ping ChildNS from ParentNS"
        status=-1
    fi
    stat=$(tst_timeout "cat /tmp/FIFO6" $NETNS_TIMEOUT)
    if [ $? -ne 0 ]; then
        tst_brkm TBROK "timeout reached!"
    fi
    if [ -z "$stat" ]; then
        stat="-1"
    fi
    if [ "$stat" != "0" ] ; then
        status=$(expr "$stat")
    fi

    exit $status
