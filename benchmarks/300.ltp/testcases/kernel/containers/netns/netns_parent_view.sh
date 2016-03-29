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

# This script verifies the contents of child sysfs is visible in parent NS.

# The test case ID, the test case count and the total number of test case

TCID=${TCID:-netns_parent_view.sh}
TST_TOTAL=1
TST_COUNT=1
export TCID
export TST_COUNT
export TST_TOTAL

    #capture parent /sys contents

    debug "INFO: Parent SYSFS view"
    ls /sys/class/net > /tmp/parent_sysfs
    tst_timeout "echo 'PROPAGATE' > /tmp/FIFO4" $NETNS_TIMEOUT
    if [ $? -ne 0 ]; then
        tst_brkm TBROK "timeout reached!"
    fi

    PROPAGATED=$(tst_timeout "cat /tmp/FIFO5" $NETNS_TIMEOUT)
    if [ $? -ne 0 ]; then
        tst_brkm TBROK "timeout reached!"
    fi
    ls /tmp/mnt/sys/class/net > /tmp/child_sysfs_in_parent
    diff /tmp/child_sysfs_in_parent /tmp/child_sysfs
    if [ $? -eq 0 ]
    then
        tst_resm TINFO "Pass: Parent is able to view child sysfs"
        status=0
    else
        tst_resm TFAIL "Fail: Parent is not able to view Child-NS sysfs"
        status=-1
    fi

    #cleanup temp files

    rm -f /tmp/child_sysfs_in_parent /tmp/child_sysfs
    umount /tmp/par_sysfs
    umount /tmp/mnt
    sleep 1
    rm -rf /tmp/par_sysfs /tmp/mnt > /dev/null 2>&1 || true
    cleanup $sshpid $vnet0
