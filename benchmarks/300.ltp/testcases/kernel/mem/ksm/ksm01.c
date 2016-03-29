/*
 * Kernel Samepage Merging (KSM)
 *
 * Basic tests were to start several programs with same and different
 * memory contents and ensure only to merge the ones with the same
 * contents. When changed the content of one of merged pages in a
 * process and to the mode "unmerging", it should discard all merged
 * pages there. Also tested it is possible to disable KSM. There are
 * also command-line options to specify the memory allocation size, and
 * number of processes have same memory contents so it is possible to
 * test more advanced things like KSM + OOM etc.
 *
 * Prerequisites:
 *
 * 1) ksm and ksmtuned daemons need to be disabled. Otherwise, it could
 *    distrub the testing as they also change some ksm tunables depends
 *    on current workloads.
 *
 * The test steps are:
 * - Check ksm feature and backup current run setting.
 * - Change run setting to 1 - merging.
 * - 3 memory allocation programs have the memory contents that 2 of
 *   them are all 'a' and one is all 'b'.
 * - Check ksm statistics and verify the content.
 * - 1 program changes the memory content from all 'a' to all 'b'.
 * - Check ksm statistics and verify the content.
 * - All programs change the memory content to all 'd'.
 * - Check ksm statistics and verify the content.
 * - Change one page of a process.
 * - Check ksm statistics and verify the content.
 * - Change run setting to 2 - unmerging.
 * - Check ksm statistics and verify the content.
 * - Change run setting to 0 - stop.
 *
 * Copyright (C) 2010  Red Hat, Inc.
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of version 2 of the GNU General Public
 * License as published by the Free Software Foundation.
 *
 * This program is distributed in the hope that it would be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 *
 * Further, this software is distributed without any warranty that it
 * is free of the rightful claim of any third person regarding
 * infringement or the like.  Any license provided herein, whether
 * implied or otherwise, applies only to this software file.  Patent
 * licenses, if any, provided herein do not apply to combinations of
 * this program with other software, or any other product whatsoever.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
 * 02110-1301, USA.
 */

#include <sys/types.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "test.h"
#include "mem.h"

char *TCID = "ksm01";
int TST_TOTAL = 1;

static int merge_across_nodes;

option_t ksm_options[] = {
	{"n:", &opt_num, &opt_numstr},
	{"s:", &opt_size, &opt_sizestr},
	{"u:", &opt_unit, &opt_unitstr},
	{NULL, NULL, NULL}
};

int main(int argc, char *argv[])
{
	int lc;
	int size = 128, num = 3, unit = 1;

	tst_parse_opts(argc, argv, ksm_options, ksm_usage);
	setup();
	for (lc = 0; TEST_LOOPING(lc); lc++) {
		tst_count = 0;
		check_ksm_options(&size, &num, &unit);
		create_same_memory(size, num, unit);
	}
	cleanup();
	tst_exit();
}

void setup(void)
{
	tst_require_root();

	if (tst_kvercmp(2, 6, 32) < 0)
		tst_brkm(TCONF, NULL, "2.6.32 or greater kernel required");
	if (access(PATH_KSM, F_OK) == -1)
		tst_brkm(TCONF, NULL, "KSM configuration is not enabled");

	/*
	 * kernel commit 90bd6fd introduced a new KSM sysfs knob
	 * /sys/kernel/mm/ksm/merge_across_nodes, setting it to '0'
	 * will prevent KSM pages being merged across numa nodes,
	 * which will cause the case fail, so we need to make sure
	 * it is enabled before testing.
	 */
	if (access(PATH_KSM "merge_across_nodes", F_OK) == 0) {
		SAFE_FILE_SCANF(NULL, PATH_KSM "merge_across_nodes",
				"%d", &merge_across_nodes);
		SAFE_FILE_PRINTF(NULL, PATH_KSM "merge_across_nodes", "1");
	}

	tst_sig(FORK, DEF_HANDLER, NULL);
	TEST_PAUSE;
}

void cleanup(void)
{
	if (access(PATH_KSM "merge_across_nodes", F_OK) == 0)
		FILE_PRINTF(PATH_KSM "merge_across_nodes",
				 "%d", merge_across_nodes);
}
