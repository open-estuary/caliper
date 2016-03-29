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

## This script checks that the parent namespace is reachable from the child
## Author:      Veerendra <veeren@linux.vnet.ibm.com>

TCID=${TCID:-netns_ch_ftp.sh}
TST_TOTAL=1
TST_COUNT=1
export TCID
export TST_COUNT
export TST_TOTAL

    ping -q -c 2 $IP1 > /dev/null
    if [ $? -ne 0 ] ; then
        tst_resm TFAIL "Pinging parent NS from child : FAIL"
        status=-1
    else
        debug "INFO: Pinging parent NS from child "
        eval netns_container_ftp.pl $IP1
        status=$?
        if [ $status -ne 0 ] ; then
            tst_resm TFAIL "ftp failed"
            status=1
        fi
    fi
    tst_timeout "echo $status > /tmp/FIFO6" $NETNS_TIMEOUT
    if [ $? -ne 0 ]; then
        tst_brkm TBROK "timeout reached!"
    fi
