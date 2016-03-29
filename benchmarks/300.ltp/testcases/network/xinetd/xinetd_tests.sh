#!/bin/sh
################################################################################
##                                                                            ##
## Copyright (c) International Business Machines  Corp., 2001                 ##
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
################################################################################
#
# File :         xinetd_tests.sh
#
# Description:   Test Basic functionality of xinetd command.
#                Test #1: xinetd starts programs that provide Internet services.
#
# Author:        Manoj Iyer, manjo@mail.utexas.edu
#
# History:       Mar 04 2003 - Created - Manoj Iyer.
#
# Function:     chk_ifexists
#
# Description:  - Check if command required for this test exits.
#
# Input:        - $1 - calling test case.
#               - $2 - command that needs to be checked.
#
# Return:       - zero on success.
#               - non-zero on failure.
chk_ifexists()
{
    which $2 > $LTPTMP/tst_xinetd.err 2>&1
    RC=$?
    if [ $RC -ne 0 ]
    then
        tst_brkm TBROK NULL "$1: command $2 not found."
    fi
    return $RC
}


# Function: init
#
# Description:  - Check if command required for this test exits.
#               - Create temporary directories required for this test.
#               - Initialize global variables.
#
# Return:       - zero on success.
#               - non-zero on failure.
init()
{
    # Initialize global variables.
    export TST_TOTAL=2
    export TCID="xinetd"
    export TST_COUNT=0
    . daemonlib.sh

    if [ -f "/usr/lib/systemd/system/telnet.socket" ]; then
        tst_brkm TCONF NULL "xinetd doesn't manage telnet"
        exit $?
    fi

    # Inititalize cleanup function.
    trap "cleanup" 0

    # create the temporary directory used by this testcase
    if [ -z $TMP ]
    then
        LTPTMP=/tmp/tst_xinetd.$$
    else
        LTPTMP=$TMP/tst_xinetd.$$
    fi

    mkdir -p $LTPTMP > /dev/null 2>&1
    RC=$?
    if [ $RC -ne 0 ]
    then
         tst_brkm TBROK NULL "INIT: Unable to create temporary directory"
         return $RC
    fi

    # sometimes the default telnet may be /usr/kerberos/bin/telnet
    TELNET_COMM='/usr/bin/telnet'

    # check if commands tst_*, xinetd, awk exists.
    chk_ifexists INIT tst_resm   || return $RC
    chk_ifexists INIT xinetd     || return $RC
    chk_ifexists INIT diff       || return $RC
    chk_ifexists INIT ip         || return $RC
    chk_ifexists INIT $TELNET_COMM || return $RC

    IPV6_ENABLED=0
    ip a | grep inet6 > /dev/null 2>&1
    if [ $? -eq 0 ]
    then
        IPV6_ENABLED=1
    fi

    # Create custom xinetd.conf file.
    # tst_xinetd.conf.1 config file has telnet service disabled.
    cat > $LTPTMP/tst_xinetd.conf.1 <<-EOF
defaults
{
    instances      = 25
    log_type       = FILE /var/log/servicelog
    log_on_success = HOST PID
    log_on_failure = HOST
    disabled       = telnet
}
EOF
RC=$?

    # tst_xinetd.conf.2 config file has telnet enabled.
    cat > $LTPTMP/tst_xinetd.conf.2 <<-EOF
defaults
{
    instances      = 25
    log_type       = FILE /var/log/servicelog
    log_on_success = HOST PID
    log_on_failure = HOST
    # disabled       = telnet
}

service telnet
{
    socket_type     = stream
    protocol        = tcp
    wait            = no
    user            = root
    server          = /usr/sbin/in.telnetd
    server_args     = -n
    no_access       =
    flags           = IPv6
}
EOF
RC=$?

    # Create expected file with telnet disabled.
    cat > $LTPTMP/tst_xinetd.exp.1 <<-EOF
telnet: connect to address 127.0.0.1: Connection refused
EOF
RC=$?

    if [ $RC -ne 0 ]
    then
        tst_brkm TBROK  NULL \
            "INIT: unable to create expected file $LTPTMP/tst_xinetd.exp.1"
        return $RC
    fi

    if [ $IPV6_ENABLED -eq 1 ]
    then
        cat > $LTPTMP/tst_xinetd.exp.1.ipv6 <<-EOF
telnet: connect to address ::1: Connection refused
EOF
RC=$?

        if [ $RC -ne 0 ]
        then
            tst_brkm TBROK NULL \
                "INIT: unable to create expected file $LTPTMP/tst_xinetd.exp.1"
        fi
    fi

    # Create expected file with telnet enabled.
    cat > $LTPTMP/tst_xinetd.exp.2 <<-EOF
Trying 127.0.0.1...
Connected to 127.0.0.1.
Escape character is '^]'.
Connection closed by foreign host.
EOF
RC=$?

    if [ $RC -ne 0 ]
    then
        tst_brkm TBROK  NULL \
            "INIT: unable to create expected file $LTPTMP/tst_xinetd.exp.2"
        return $RC
    fi

    if [ $IPV6_ENABLED -eq 1 ]
    then
        cat > $LTPTMP/tst_xinetd.exp.2.ipv6 <<-EOF
Trying ::1...
Connected to ::1.
Escape character is '^]'.
Connection closed by foreign host.
EOF
RC=$?

        if [ $RC -ne 0 ]
        then
            tst_brkm TBROK NULL \
                "INIT: unable to create expected file $LTPTMP/tst_xinetd.exp.2.ipv6"
        fi
    fi

    return $RC
}


# Function:     cleanup
#
# Description:  - remove temporaty files and directories.
#
# Return:       - zero on success.
#               - non-zero on failure.
cleanup()
{
    # restore the original xinetd.conf if a back up exits.
    if [ -f /etc/xinetd.conf.orig ]
    then
        mv /etc/xinetd.conf.orig /etc/xinetd.conf \
            > $LTPTMP/tst_xinetd.err 2>&1
        RC=$?
        if [ $RC -ne 0 ]
        then
            tst_res TINFO $LTPTMP/tst_xinetd.err \
            "CLEANUP: failed restoring original xinetd.conf RC=$RC. Details:"
        fi

        sleep 1s

        # restoring original services
        restart_daemon xinetd > $LTPTMP/tst_xinetd.err 2>&1
        RC=$?
        if [ $RC -ne 0 ]
        then
            tst_res TINFO $LTPTMP/tst_xinetd.err \
            "CLEANUP: failed restoring original services RC=$RC. Details:"
        fi
    fi

    # remove all the temporary files created by this test.
    tst_resm TINFO "CLEAN: removing $LTPTMP"
    rm -fr $LTPTMP
}


# Function:     test01
#
# Description:  - Test that xinetd reads the configuration file and starts or
#                 stops services.
#               - restart xinetd with configuration file with telnet disabled.
#               - telnet to locahost should fail.
#               - restart xinetd with configuration file with telnet enabled.
#               - telnet to locahost should work.
#
# Return:       - zero on success.
#               - non-zero on failure.
test01()
{
    TCID=xinetd01
    TST_COUNT=1
    nhops=0             # Number of hops required to get to host.

    tst_resm TINFO "Test #1: restart xinetd with telnet disabled."

    # create a backup of the original xinetd.conf file.
    mv /etc/xinetd.conf /etc/xinetd.conf.orig > $LTPTMP/tst_xinetd.err 2>&1
    RC=$?
    if [ $RC -ne 0 ]
    then
        tst_brk TBROK $LTPTMP/tst_xinetd.err NULL \
            "Test #1: Failed while backing up original xinetd.conf. Details"
        return $RC
    fi

    # install the new config file with telnet disabled.
    mv $LTPTMP/tst_xinetd.conf.1 /etc/xinetd.conf > $LTPTMP/tst_xinetd.err 2>&1
    RC=$?
    if [ $RC -ne 0 ]
    then
        tst_brk TBROK $LTPTMP/tst_xinetd.err NULL \
            "Test #1: Failed installing new xinetd.conf in /etc. Details:"
        return $RC
    fi

    tst_resm TINFO "Test #1: new xinetd.conf installed with telnet disabled."

    sleep 1s

    # restart xinetd to re-start the services
    restart_daemon xinetd > $LTPTMP/tst_xinetd.out 2>&1
    RC=$?
    if [ $RC -ne 0 ]
    then
        tst_res TFAIL $LTPTMP/tst_xinetd.out \
       "Test #1: unable to restart service with telnet disabled. Details:"
        return $RC
    else
        # even if xinetd restart has zero exit value,
        # make certain there was no failure.
        grep -i "fail" $LTPTMP/tst_xinetd.out > $LTPTMP/tst_xinetd.err 2>&1
        RC=$?
        if [ $RC -eq 0 ]
        then
            tst_res TFAIL $LTPTMP/tst_xinetd.err \
                "Test #1: xinetd failed to restart. Details"
            return $RC
        else
            RC=0
            tst_resm TINFO \
                "Test #1: xinetd re-started successfully with telnet disabled."
        fi
    fi

    # Not checking for exit code from telnet command because telnet is
    # not terminated by the test gracefully.
    if [ $IPV6_ENABLED -eq 1 ]
    then
        tst_retry "echo '' | $TELNET_COMM ::1 2>$LTPTMP/tst_xinetd.out.ipv6 \
            1>/dev/null"
        diff -iwB $LTPTMP/tst_xinetd.out.ipv6  $LTPTMP/tst_xinetd.exp.1.ipv6 \
            > $LTPTMP/tst_xinetd.err.ipv6 2>&1
        RC=$?
        if [ $RC -ne 0 ]
        then
            tst_res TFAIL $LTPTMP/tst_xinetd.err.ipv6 \
                "Test #1: with telnet diabled expected out differs RC=$RC. Details:"
            return $RC
        fi
    fi

    tst_retry "echo "" | $TELNET_COMM 127.0.0.1 2>$LTPTMP/tst_xinetd.out \
        1>/dev/null"
    diff -iwB $LTPTMP/tst_xinetd.out  $LTPTMP/tst_xinetd.exp.1 \
        > $LTPTMP/tst_xinetd.err 2>&1
    RC=$?
    if [ $RC -ne 0 ]
    then
        tst_res TFAIL $LTPTMP/tst_xinetd.err \
            "Test #1: with telnet diabled expected out differs RC=$RC. Details:"
        return $RC
    fi

    tst_resm TINFO "Test #1: restart xinetd with telnet enabled."
    # install the xinetd config file with telnet enabled.
    mv $LTPTMP/tst_xinetd.conf.2 /etc/xinetd.conf > $LTPTMP/tst_xinetd.err 2>&1
    RC=$?
    if [ $RC -ne 0 ]
    then
        tst_brk TBROK $LTPTMP/tst_xinetd.err NULL \
            "Test #1: Failed installing new xinetd.conf in /etc. Details:"
        return $RC
    fi

    tst_resm TINFO "Test #1: new xinetd.conf installed with telnet enabled."

    sleep 1s

    # restart services.
    restart_daemon xinetd > $LTPTMP/tst_xinetd.out 2>&1
    RC=$?
    if [ $RC -ne 0 ]
    then
        tst_res TFAIL $LTPTMP/tst_xinetd.out \
            "Test #1: unable to restart services with telnet enabled. Details:"
        return $RC
    else
        # even if restart has a zero exit value double check for failure.
        grep -i "fail" $LTPTMP/tst_xinetd.out > $LTPTMP/tst_xinetd.err 2>&1
        RC=$?
        if [ $RC -eq 0 ]
        then
            tst_res TFAIL $LTPTMP/tst_xinetd.err \
                "Test #1: xinetd failed to restart. Details"
            return $RC
        else
            RC=0
            tst_resm TINFO \
                "Test #1: xinetd re-started successfully with telnet enabled."
        fi
    fi

    # Not checking for exit code from telnet command because telnet is
    # not terminated by the test gracefully.
    if [ $IPV6_ENABLED -eq 1 ]
    then
        tst_retry "echo '' | $TELNET_COMM ::1 2>$LTPTMP/tst_xinetd.out.ipv6 2>&1"
        diff -iwB $LTPTMP/tst_xinetd.out.ipv6  $LTPTMP/tst_xinetd.exp.2.ipv6 \
            > $LTPTMP/tst_xinetd.err.ipv6 2>&1
        RC=$?
        if [ $RC -ne 0 ]
        then
            tst_res TFAIL $LTPTMP/tst_xinetd.err.ipv6 \
                "Test #1: with telnet diabled expected out differs RC=$RC. Details:"
            return $RC
        else
            tst_resm TPASS \
            "Test #1: xinetd reads the config file and starts or stops IPv6 services."
        fi
    fi

    test_retry "echo '' | $TELNET_COMM 127.0.0.1 2>$LTPTMP/tst_xinetd.out 2>&1"

    diff -iwB $LTPTMP/tst_xinetd.out  $LTPTMP/tst_xinetd.exp.2 \
        > $LTPTMP/tst_xinetd.err 2>&1
    RC=$?
    if [ $RC -ne 0 ]
    then
        tst_res TFAIL $LTPTMP/tst_xinetd.err \
            "Test #1: expected output differes from actual. Details:"
        return $RC
    else
        tst_resm TPASS \
        "Test #1: xinetd reads the config file and starts or stops services."
    fi

    return $RC
}


# Function:    main
#
# Description:    - Execute all tests and report results.
#
# Exit:            - zero on success
#               - non-zero on failure.

init || exit $?

test01 || RC=$?

exit $RC
