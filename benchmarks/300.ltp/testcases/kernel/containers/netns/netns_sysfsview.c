
/*************************************************************************
* Copyright (c) International Business Machines Corp., 2008
* This program is free software; you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation; either version 2 of the License, or
* (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
* the GNU General Public License for more details.
* You should have received a copy of the GNU General Public License
* along with this program; if not, write to the Free Software
* Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
*
***************************************************************************/

/* ============================================================================
* This testcase uses the libnetns.c from the lib to create network NS1.
* In libnetns.c it uses 2 scripts parentns.sh and childns.sh to create this.
*
* This testcase verifies sysfs contents of parentNS is visible from child NS.
* Also it checks the sysfs contents of the child are visible from the parent NS.
* On Success it returns PASS else returns FAIL
*
* Scripts used: parent_share.sh parent_view.sh child_propagate.sh
*               parentns.sh childns.sh
*
*
* Authors:      Poornima Nayak <poornima.nayak@in.ibm.com>
*               Veerendra C <vechandr@in.ibm.com>
*                      31/07/2008
* ============================================================================*/
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/wait.h>
#include "common.h"

const char *TCID = "netns_sysfsview";

#define SCRIPT "netns_parent_share.sh"

int main(void)
{
	int ret, status = 0;

	/* Parent should be able to view child sysfs and vice versa */
	ret = system(SCRIPT);
	status = WEXITSTATUS(ret);
	if (ret == -1 || status != 0) {
		printf("Error while executing the script %s\n", SCRIPT);
		fflush(stdout);
		exit(1);
	}

	status = create_net_namespace("netns_parent_view.sh", "netns_child_propagate.sh");
	return status;
}
