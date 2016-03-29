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
 * Test Description:
 *  Verify that access() succeeds to check the existance of a file if
 *  search access is permitted on the pathname of the specified file.
 *
 *  07/2001 Ported by Wayne Boyer
 */

#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>
#include <errno.h>
#include <fcntl.h>
#include <string.h>
#include <signal.h>
#include <sys/stat.h>
#include <pwd.h>

#include "test.h"

#define TESTDIR		"testdir"
#define TESTFILE	"testdir/testfile"
#define DIR_MODE	(S_IRWXU | S_IRUSR | S_IXUSR | S_IRGRP | S_IXGRP)
#define FILE_MODE	(S_IRUSR | S_IWUSR | S_IRGRP | S_IROTH)

char *TCID = "access04";
int TST_TOTAL = 1;

static const char nobody_uid[] = "nobody";
static struct passwd *ltpuser;

static void setup(void);
static void cleanup(void);

int main(int ac, char **av)
{
	struct stat stat_buf;
	int lc;

	tst_parse_opts(ac, av, NULL, NULL);

	setup();

	for (lc = 0; TEST_LOOPING(lc); lc++) {
		tst_count = 0;

		TEST(access(TESTFILE, F_OK));

		if (TEST_RETURN == -1) {
			tst_resm(TFAIL | TTERRNO, "access(%s, F_OK) failed",
				 TESTFILE);
			continue;
		}

		if (stat(TESTFILE, &stat_buf) < 0) {
			tst_resm(TFAIL | TERRNO, "stat(%s) failed",
				 TESTFILE);
		} else {
			tst_resm(TPASS, "functionality of "
				 "access(%s, F_OK) ok", TESTFILE);
		}
	}

	cleanup();
	tst_exit();
}

static void setup(void)
{
	int fd;

	tst_sig(NOFORK, DEF_HANDLER, cleanup);
	tst_require_root();

	ltpuser = getpwnam(nobody_uid);
	if (ltpuser == NULL)
		tst_brkm(TBROK | TERRNO, NULL, "getpwnam failed");

	if (setuid(ltpuser->pw_uid) == -1)
		tst_brkm(TINFO | TERRNO, NULL, "setuid failed");

	TEST_PAUSE;
	tst_tmpdir();

	if (mkdir(TESTDIR, DIR_MODE) < 0)
		tst_brkm(TBROK | TERRNO, cleanup, "mkdir(%s, %#o) failed",
			 TESTDIR, DIR_MODE);

	if (chmod(TESTDIR, DIR_MODE) < 0)
		tst_brkm(TBROK | TERRNO, cleanup, "chmod(%s, %#o) failed",
			 TESTDIR, DIR_MODE);

	fd = open(TESTFILE, O_RDWR | O_CREAT, FILE_MODE);
	if (fd == -1)
		tst_brkm(TBROK | TERRNO, cleanup,
			 "open(%s, O_RDWR|O_CREAT, %#o) failed",
			 TESTFILE, FILE_MODE);

	if (close(fd) == -1)
		tst_brkm(TBROK | TERRNO, cleanup, "close(%s) failed", TESTFILE);

	if (chmod(TESTFILE, 0) < 0)
		tst_brkm(TBROK | TERRNO, cleanup,
			 "chmod(%s, 0) failed", TESTFILE);
}

static void cleanup(void)
{
	tst_rmdir();
}
