#!/bin/sh
# Copyright (C) 2012-2014, Linaro Limited.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
# Author: Avik Sil <avik.sil@linaro.org>
# Author: Milosz Wasilewski <milosz.wasilewski@linaro.org>

test_perf_record()
{
    TCID="perf record test"
    test_prequisite
    if [ $result -eq 1 ]; then
        echo "$TCID : fail"
        return 
    fi
    # Test 'perf record'
    echo "Performing perf record test..."
    perf record -e cycles -o perf-lava-test.data stress -c 4 -t 10  2>&1 | tee perf-record.log
    samples=`grep -ao "[0-9]\+[ ]\+samples" perf-record.log| cut -f 1 -d' '`
    if [ $samples -gt 1 ]; then
        echo "$TCID : pass"
    else
        echo "$TCID : fail"
    fi
    rm perf-record.log
}

test_prequisite()
{
    result=0	
    output=$(stress|grep 'Usage')
    if [ "$output"x = ""x ]; then 
        echo "you need to install stress first"
        echo '-1'
	result=1
    fi
    output=$(perf | grep 'usage')
    if [ "$output"x = ""x ]; then
        echo "you need to install perf first"
        echo '-1'
	result=1
    fi
}

test_perf_report()
{
    TCID="perf report test"
    test_prequisite
    if [ $result -eq 1 ]; then
        echo "$TCID : fail"
        return 
    fi
    # Test 'perf report'
    echo "Performing perf report test..."
    if [ ! -f perf-lava-test.data ]; then
        perf record -e cycles -o perf-lava-test.data stress -c 4 -t 10  2>&1 | tee perf-record.log
    fi
    perf report -i perf-lava-test.data 2>&1 | tee perf-report.log
    pcnt_samples=`grep -c -e "^[ ]\+[0-9]\+.[0-9]\+%" perf-report.log`
    if [ $pcnt_samples -gt 1 ]; then
        echo "$TCID : pass"
    else
        echo "$TCID : fail"
    fi
    rm perf-report.log perf-lava-test.data
}

test_perf_stat()
{
    TCID="perf stat test"
    test_prequisite
    if [ $result -eq 1 ]; then
        echo "$TCID : fail"
        return 
    fi
    # Test 'perf stat'
    echo "Performing perf stat test..."
    perf stat -e cycles stress -c 4 -t 10 2>&1 | tee perf-stat.log
    cycles=`grep -o "[0-9,]\+[ ]\+cycles" perf-stat.log | sed 's/,//g' | cut -f 1 -d' '`
    if [ -z "$cycles" ]; then
        echo "$TCID : skip"
    else
        if [ $cycles -gt 1 ]; then
            echo "$TCID : pass"
        else
            echo "$TCID : fail"
        fi
    fi
    rm perf-stat.log
}

test_perf_test()
{
    test_prequisite
    if [ $result -eq 1 ]; then
        echo "perf test : fail"
        echo "-1"
	return
    fi
    # Test 'perf test'
    echo "Performing 'perf test'..."
    perf test -v 2>&1 | sed -e 's/FAILED!/fail/g' -e 's/Ok/pass/g' -e 's/:/ :/g'
}

# Test user id
if [ `whoami` != 'root' ] ; then
    echo "You must be the superuser to run this script" >&2
    exit 1
fi

case $1 in 
    "1" ) 
        test_perf_record
        ;;
    "2" )
        test_perf_report
        ;;
    "3" )
        test_perf_stat
        ;;
    "4" )
        test_perf_test
        ;;
esac

