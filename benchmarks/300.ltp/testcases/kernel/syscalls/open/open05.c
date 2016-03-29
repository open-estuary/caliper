/*
 *
 *   Copyright (c) International Business Machines  Corp., 2001
 *
 *   This program is free software;  you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation; either version 2 of the License, or
 *   (at your option) any later version.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY;  without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See
 *   the GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with this program;  if not, write to the Free Software
 *   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
 */

/*
 * DESCRIPTION
 *	Testcase to check open(2) sets errno to EACCES correctly.
 *
 * ALGORITHM
 *	Create a file owned by root with no read permission for other users.
 *	Attempt to open it as ltpuser(1). The attempt should fail with EACCES.
 * RESTRICTION
 *	Must run test as root.
 */
#include <errno.h>
#include <pwd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include "test.h"
#include "usctest.h"

static char user1name[] = "nobody";

char *TCID = "open05";
int TST_TOTAL = 1;

extern struct passwd *my_getpwnam(char *);
static char fname[20];
static struct passwd *nobody;
static int fd;

static int exp_enos[] = { EACCES, 0 };

static void cleanup(void);
static void setup(void);

int main(int ac, char **av)
{
	int lc;
	const char *msg;
	int e_code, status, retval = 0;
	pid_t pid;

	msg = parse_opts(ac, av, NULL, NULL);
	if (msg != NULL)
		tst_brkm(TBROK, NULL, "OPTION PARSING ERROR - %s", msg);

	setup();

	TEST_EXP_ENOS(exp_enos);

	for (lc = 0; TEST_LOOPING(lc); lc++) {
		/* reset tst_count in case we are looping */
		tst_count = 0;

		pid = FORK_OR_VFORK();
		if (pid == -1)
			tst_brkm(TBROK, cleanup, "fork() failed");

		if (pid == 0) {
			if (seteuid(nobody->pw_uid) == -1) {
				tst_resm(TWARN, "seteuid() failed, errno: %d",
					 errno);
			}

			TEST(open(fname, O_RDWR));

			if (TEST_RETURN != -1) {
				tst_resm(TFAIL, "open succeeded unexpectedly");
				continue;
			}

			TEST_ERROR_LOG(TEST_ERRNO);

			if (TEST_ERRNO != EACCES) {
				retval = 1;
				tst_resm(TFAIL, "Expected EACCES got %d",
					 TEST_ERRNO);
			} else {
				tst_resm(TPASS, "open returned expected "
					 "EACCES error");
			}

			/* set the id back to root */
			if (seteuid(0) == -1)
				tst_resm(TWARN, "seteuid(0) failed");

			exit(retval);

		} else {
			/* wait for the child to finish */
			wait(&status);
			/* make sure the child returned a good exit status */
			e_code = status >> 8;
			if ((e_code != 0) || (retval != 0))
				tst_resm(TFAIL, "Failures reported above");

			close(fd);
			cleanup();

		}
	}

	tst_exit();
}

static void setup(void)
{
	tst_require_root(NULL);

	tst_sig(FORK, DEF_HANDLER, cleanup);

	TEST_PAUSE;

	/* make a temporary directory and cd to it */
	tst_tmpdir();

	sprintf(fname, "file.%d", getpid());

	nobody = my_getpwnam(user1name);

	fd = open(fname, O_RDWR | O_CREAT, 0700);
	if (fd == -1)
		tst_brkm(TBROK, cleanup, "open() failed, errno: %d", errno);
}

static void cleanup(void)
{
	TEST_CLEANUP;

	unlink(fname);

	/* delete the test directory created in setup() */
	tst_rmdir();
}
