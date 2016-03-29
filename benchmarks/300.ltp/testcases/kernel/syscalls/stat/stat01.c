/*
 * Copyright (c) International Business Machines  Corp., 2001
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
 * Test Description:
 *  Verify that, stat(2) succeeds to get the status of a file and fills the
 *  stat structure elements.
 *
 * Expected Result:
 *  stat() should return value 0 on success and fills the stat structure
 *  elements with the specified 'file' information.
 *
 * Algorithm:
 *  Setup:
 *   Setup signal handling.
 *   Create temporary directory.
 *   Pause for SIGUSR1 if option specified.
 *
 *  Test:
 *   Loop if the proper options are given.
 *   Execute system call
 *   Check return code, if system call failed (return=-1)
 *   	Log the errno and Issue a FAIL message.
 *   Otherwise,
 *   	Verify the Functionality of system call
 *      if successful,
 *      	Issue Functionality-Pass message.
 *      Otherwise,
 *		Issue Functionality-Fail message.
 * History
 *	07/2001 John George
 *		-Ported
 */
#include <stdio.h>
#include <sys/types.h>
#include <sys/fcntl.h>
#include <sys/stat.h>
#include <errno.h>
#include <string.h>
#include <signal.h>
#include <pwd.h>

#include "test.h"
#include "usctest.h"

#define FILE_MODE	0644
#define TESTFILE	"testfile"
#define FILE_SIZE       1024
#define BUF_SIZE	256
#define MASK		0777

char *TCID = "stat01";
int TST_TOTAL = 1;
int exp_enos[] = { 0 };

uid_t user_id;
gid_t group_id;
char nobody_uid[] = "nobody";
struct passwd *ltpuser;

static void setup(void);
static void cleanup(void);

int main(int ac, char **av)
{
	struct stat stat_buf;
	int lc;
	const char *msg;

	if ((msg = parse_opts(ac, av, NULL, NULL)) != NULL)
		tst_brkm(TBROK, NULL, "OPTION PARSING ERROR - %s", msg);

	setup();

	TEST_EXP_ENOS(exp_enos);

	for (lc = 0; TEST_LOOPING(lc); lc++) {

		tst_count = 0;

		/*
		 * Call stat(2) to get the status of
		 * specified 'file' into stat structure.
		 */
		TEST(stat(TESTFILE, &stat_buf));

		if (TEST_RETURN == -1) {
			TEST_ERROR_LOG(TEST_ERRNO);
			tst_resm(TFAIL,
				 "stat(%s, &stat_buf) Failed, errno=%d : %s",
				 TESTFILE, TEST_ERRNO, strerror(TEST_ERRNO));
		} else {
			stat_buf.st_mode &= ~S_IFREG;
			/*
			 * Verify the data returned by stat(2)
			 * aganist the expected data.
			 */
			if ((stat_buf.st_uid != user_id) ||
			    (stat_buf.st_gid != group_id) ||
			    (stat_buf.st_size != FILE_SIZE) ||
			    ((stat_buf.st_mode & MASK) != FILE_MODE)) {
				tst_resm(TFAIL, "Functionality of "
					 "stat(2) on '%s' Failed",
					 TESTFILE);
			} else {
				tst_resm(TPASS, "Functionality of "
					 "stat(2) on '%s' Succcessful",
					 TESTFILE);
			}
		}
		tst_count++;
	}

	cleanup();
	tst_exit();
}

void setup(void)
{
	int i, fd;
	char tst_buff[BUF_SIZE];
	int wbytes;
	int write_len = 0;

	tst_require_root(NULL);

	tst_sig(NOFORK, DEF_HANDLER, cleanup);

	/* Switch to nobody user for correct error code collection */
	ltpuser = getpwnam(nobody_uid);
	if (setuid(ltpuser->pw_uid) == -1) {
		tst_resm(TINFO, "setuid failed to "
			 "to set the effective uid to %d", ltpuser->pw_uid);
		perror("setuid");
	}

	/* Pause if that option was specified
	 * TEST_PAUSE contains the code to fork the test with the -i option.
	 * You want to make sure you do this before you create your temporary
	 * directory.
	 */
	TEST_PAUSE;

	tst_tmpdir();

	if ((fd = open(TESTFILE, O_RDWR | O_CREAT, FILE_MODE)) == -1) {
		tst_brkm(TBROK, cleanup,
			 "open(%s, O_RDWR|O_CREAT, %#o) Failed, errno=%d : %s",
			 TESTFILE, FILE_MODE, errno, strerror(errno));
	}

	/* Fill the test buffer with the known data */
	for (i = 0; i < BUF_SIZE; i++)
		tst_buff[i] = 'a';

	/* Write to the file 1k data from the buffer */
	while (write_len < FILE_SIZE) {
		if ((wbytes = write(fd, tst_buff, sizeof(tst_buff))) <= 0) {
			tst_brkm(TBROK, cleanup,
				 "write(2) on %s Failed, errno=%d : %s",
				 TESTFILE, errno, strerror(errno));
		} else {
			write_len += wbytes;
		}
	}

	/* Close the testfile created */
	if (close(fd) == -1) {
		tst_resm(TWARN, "close(%s) Failed, errno=%d : %s",
			 TESTFILE, errno, strerror(errno));
	}

	/* Get the uid/gid of the process */
	user_id = getuid();
	group_id = getgid();
}

static void cleanup(void)
{
	TEST_CLEANUP;

	tst_rmdir();
}
