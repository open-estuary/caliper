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
 * NAME
 *	getcwd01
 *
 * DESCRIPTION
 *	Testcase to test that getcwd(2) sets errno correctly.
 *
 * ALGORITHM
 *	Test 1: Call getcwd(2) with a buf pointing outside the address space of
 *		 process, and a valid size, and expect EFAULT to be
 *		 set in errno.
 *	Test 2: Call getcwd(2) with buf = NULL, size = -1, and expect ENOMEM
 *		 to be set in errno.
 *	Test 3: Call getcwd(2) with a valid buf, and size = 0, and expect
 *		 EINVAL to be set in errno.
 *	Test 4: Call getcwd(2) on the root directory, and set size to 1, expect
 *		 ERANGE to be set in errno.
 *
 * USAGE:  <for command-line>
 *  getcwd01 [-c n] [-e] [-i n] [-I x] [-P x] [-t]
 *     where,  -c n : Run n copies concurrently.
 *             -e   : Turn on errno logging.
 *             -i n : Execute test n times.
 *             -I x : Execute test for x seconds.
 *             -P x : Pause for x seconds between iterations.
 *             -t   : Turn on syscall timing.
 *
 * HISTORY
 *	07/2001 Ported by Wayne Boyer
 *
 * RESTRICTIONS
 *	NONE
 */
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include "test.h"

char *TCID = "getcwd01";
char buf[100];

void cleanup(void);
void setup(void);
void setup_test4(void);

struct test_case_t {
	char *desc;
	void (*setupfunc) ();
	char *buf;
	int size;
	int exp_errno;
	char *exp_retval;
} testcases[] = {
#ifndef UCLINUX
	/* Skip since uClinux does not implement memory protection */
	{
	"Test for EFAULT", NULL, (void *)-1, BUFSIZ, EFAULT, NULL},
#endif
	{
	"Test for ENOMEM", NULL, NULL, -1, ENOMEM, NULL}, {
	"Test for EINVAL", NULL, buf, 0, EINVAL, NULL}, {
	"Test for ERANGE", (void *)setup_test4, buf, 1, ERANGE, NULL}
};

int TST_TOTAL = ARRAY_SIZE(testcases);

int main(int ac, char **av)
{
	int i;
	int lc;
	char *test_erg;

	tst_parse_opts(ac, av, NULL, NULL);
	setup();

	/*
	 * The following loop checks looping state if -i option given
	 */
	for (lc = 0; TEST_LOOPING(lc); lc++) {
		tst_count = 0;

		for (i = 0; i < TST_TOTAL; ++i) {
			tst_resm(TINFO, "%s", testcases[i].desc);

			if (testcases[i].setupfunc != NULL) {
				testcases[i].setupfunc();
			}

			errno = 0;
			test_erg = getcwd(testcases[i].buf, testcases[i].size);
			TEST_ERRNO = errno;

			if (test_erg != testcases[i].exp_retval) {
				tst_resm(TFAIL, "getcwd(2) failed to return"
					 "expected value, expected: %p, "
					 "got: %p", testcases[i].exp_retval,
					 test_erg);
				continue;
			}
			if (TEST_ERRNO != testcases[i].exp_errno) {
				tst_resm(TFAIL, "getcwd returned unexpected "
					 "errno, expected: %d, got: %d",
					 testcases[i].exp_errno, TEST_ERRNO);
				continue;
			}
			tst_resm(TPASS, "Test case %d PASSED", i + 1);
		}
	}
	cleanup();

	tst_exit();
}

void setup_test4(void)
{
	chdir("/");
}

void setup(void)
{
	tst_sig(NOFORK, DEF_HANDLER, cleanup);

	TEST_PAUSE;

	/* create a test directory and cd into it */
	tst_tmpdir();
}

void cleanup(void)
{
	/* remove the test directory */
	tst_rmdir();
}
