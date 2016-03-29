/*
 * Copyright (c) International Business Machines  Corp., 2001
 * Copyright (c) 2012 Cyril Hrubis <chrubis@suse.cz>
 *
 * This program is free software;  you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY;  without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See
 * the GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program;  if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
 */

/*
 * Testcase to check creat(2) sets ETXTBSY correctly.
 */

#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <errno.h>
#include <fcntl.h>
#include <libgen.h>
#include <stdio.h>
#include "test.h"

#define TEST_APP "creat07_child"

char *TCID = "creat07";
int TST_TOTAL = 1;

static void setup(void);
static void cleanup(void);

int main(int ac, char **av)
{
	int lc;
	pid_t pid;

	tst_parse_opts(ac, av, NULL, NULL);

	setup();

	for (lc = 0; TEST_LOOPING(lc); lc++) {

		tst_count = 0;

		if ((pid = FORK_OR_VFORK()) == -1)
			tst_brkm(TBROK|TERRNO, cleanup, "fork #1 failed");

		if (pid == 0) {
			char *av[2];
			av[0] = TEST_APP;
			av[1] = NULL;
			(void)execve(TEST_APP, av, NULL);
			perror("execve failed");
			exit(1);
		}

		TST_SAFE_CHECKPOINT_WAIT(NULL, 0);

		TEST(creat(TEST_APP, O_WRONLY));

		if (TEST_RETURN != -1) {
			tst_resm(TFAIL, "creat succeeded");
		} else {
			if (TEST_ERRNO == ETXTBSY)
				tst_resm(TPASS, "creat received EXTBSY");
			else
				tst_resm(TFAIL | TTERRNO, "creat failed with "
				                         "unexpected error");
		}

		if (kill(pid, SIGKILL) == -1)
			tst_resm(TINFO | TERRNO, "kill failed");

		if (wait(NULL) == -1)
			tst_brkm(TBROK|TERRNO, cleanup, "wait failed");
	}

	cleanup();
	tst_exit();
}

static void setup(void)
{
	tst_sig(FORK, DEF_HANDLER, cleanup);

	tst_tmpdir();

	TST_CHECKPOINT_INIT(tst_rmdir);

	TST_RESOURCE_COPY(cleanup, TEST_APP, NULL);

	TEST_PAUSE;
}

static void cleanup(void)
{
	tst_rmdir();
}
