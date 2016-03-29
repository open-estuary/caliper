#############################################################################
##
## Copyright (c) International Business Machines  Corp., 2007
##
## This program is free software;  you can redistribute it and#or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
## or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
## for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program;  if not, write to the Free Software
## Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
##
#############################################################################
#
# Author         Pradeep Kumar Surisetty, pradeepkumars@in.ibm.com
#
# History        Nov 27 2007 -created- pradeep kumar surisetty
#! /bin/sh
#
# File :         numa_test.sh


#!/bin/sh
x=0
chk_ifexist()
{
if [ ! -d /sys/devices/system/node ]
then
x=0
else
x=$(ls /sys/devices/system/node | wc -l)
fi
if [ $x -gt 1 ]
then
	if [ ! -f /usr/include/numa.h ]
	then
		echo no;
 	else
		echo yes;
	fi
else
        echo no;     #numa is not present

fi
}
chk_ifexist

