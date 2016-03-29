/*
 * Copyright (c) 2014 Fujitsu Ltd.
 * Author: Xing Gu <gux.fnst@cn.fujitsu.com>
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of version 2 of the GNU General Public License as
 * published by the Free Software Foundation.
 *
 * This program is distributed in the hope that it would be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, write the Free Software Foundation, Inc.,
 * 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 */
/*
 * Description:
 *   Verify that,
 *   1) mprotect() succeeds to set a region of memory with no access,
 *      when 'prot' is set to PROT_NONE. An attempt to access the contents
 *      of the region gives rise to the signal SIGSEGV.
 *   2) mprotect() succeeds to set a region of memory to be executed, when
 *      'prot' is set to PROT_EXEC.
 */

#include <signal.h>
#include <setjmp.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <sys/mman.h>
#include <stdlib.h>

#include "test.h"
#include "usctest.h"
#include "safe_macros.h"

static void sighandler(int sig);

static void setup(void);
static void cleanup(void);

static void testfunc_protnone(void);

static void exec_func(void);
static void testfunc_protexec(void);

static void (*testfunc[])(void) = { testfunc_protnone, testfunc_protexec };

char *TCID = "mprotect04";
int TST_TOTAL = ARRAY_SIZE(testfunc);

static volatile int sig_caught;
static sigjmp_buf env;

int main(int ac, char **av)
{
	int lc;
	int i;
	const char *msg;

	msg = parse_opts(ac, av, NULL, NULL);
	if (msg != NULL)
		tst_brkm(TBROK, NULL, "OPTION PARSING ERROR - %s", msg);

	setup();

	for (lc = 0; TEST_LOOPING(lc); lc++) {
		tst_count = 0;

		for (i = 0; i < TST_TOTAL; i++)
			(*testfunc[i])();
	}

	cleanup();
	tst_exit();
}

static void sighandler(int sig)
{
	sig_caught = sig;
	siglongjmp(env, 1);
}

static void setup(void)
{
	tst_sig(NOFORK, sighandler, cleanup);

	TEST_PAUSE;
}

static void testfunc_protnone(void)
{
	char *addr;
	int page_sz;

	sig_caught = 0;

	page_sz = getpagesize();

	addr = SAFE_MMAP(cleanup, 0, page_sz, PROT_READ | PROT_WRITE,
					 MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);

	/* Change the protection to PROT_NONE. */
	TEST(mprotect(addr, page_sz, PROT_NONE));

	if (TEST_RETURN == -1) {
		tst_resm(TFAIL | TTERRNO, "mprotect failed");
	} else {
		if (sigsetjmp(env, 1) == 0)
			addr[0] = 1;

		switch (sig_caught) {
		case SIGSEGV:
			tst_resm(TPASS, "test PROT_NONE for mprotect success");
		break;
		case 0:
			tst_resm(TFAIL, "test PROT_NONE for mprotect failed");
		break;
		default:
			tst_brkm(TBROK, cleanup,
			         "received an unexpected signal: %d",
			         sig_caught);
		}
	}

	SAFE_MUNMAP(cleanup, addr, page_sz);
}

static void exec_func(void)
{
	return;
}

static void testfunc_protexec(void)
{
	int page_sz;
	int (*func)(void);

	sig_caught = 0;

	page_sz = getpagesize();

	func = SAFE_MMAP(cleanup, 0, page_sz, PROT_READ | PROT_WRITE,
					 MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);

	memcpy(func, exec_func, page_sz);

	/* Change the protection to PROT_EXEC. */
	TEST(mprotect(func, page_sz, PROT_EXEC));

	if (TEST_RETURN == -1) {
		tst_resm(TFAIL | TTERRNO, "mprotect failed");
	} else {
		if (sigsetjmp(env, 1) == 0)
			(*func)();

		switch (sig_caught) {
		case SIGSEGV:
			tst_resm(TFAIL, "test PROT_EXEC for mprotect failed");
		break;
		case 0:
			tst_resm(TPASS, "test PROT_EXEC for mprotect success");
		break;
		default:
			tst_brkm(TBROK, cleanup,
			         "received an unexpected signal: %d",
			         sig_caught);
		}
	}

	SAFE_MUNMAP(cleanup, func, page_sz);
}

static void cleanup(void)
{
	TEST_CLEANUP;
}
