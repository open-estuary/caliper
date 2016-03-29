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
 *	waitpid13.c
 *
 * DESCRIPTION
 *	Tests to see if pid's returned from fork and waitpid are same
 *
 * ALGORITHM
 *	Check proper functioning of waitpid with pid = 0 and < -1 with arg
 *	WUNTRACED
 *
 * USAGE:  <for command-line>
 *      waitpid13 [-c n] [-t]
 *      where,  -c n : Run n copies concurrently.
 *              -t   : Turn on syscall timing.
 *
 * History
 *	07/2001 John George
 *		-Ported
 *      04/2002 wjhuie sigset cleanups
 *
 * Restrictions
 *	None
 */

#include <sys/types.h>
#include <signal.h>
#include <errno.h>
#include <sys/wait.h>
#include "test.h"

#define	MAXKIDS	8

char *TCID = "waitpid13";
int TST_TOTAL = 1;

volatile int intintr;
static void setup(void);
static void cleanup(void);
static void inthandlr();
static void wait_for_parent(void);
static void do_exit(void);
static void setup_sigint(void);
#ifdef UCLINUX
static void do_exit_uclinux(void);
#endif

static int fail;

int main(int ac, char **av)
{
	int kid_count, ret_val, status;
	int i, j, k, found;
	int group1, group2;
	int fork_kid_pid[MAXKIDS], wait_kid_pid[MAXKIDS];
	int pid;

	tst_parse_opts(ac, av, NULL, NULL);

#ifdef UCLINUX
	maybe_run_child(&do_exit_uclinux, "");
#endif

	setup();

	tst_count = 0;
	fail = 0;

	/*
	 * Need to have test run from child as test driver causes
	 * test to be a session leader and setpgrp fails.
	 */
	pid = FORK_OR_VFORK();
	if (pid > 0) {
		waitpid(pid, &status, 0);
		if (WEXITSTATUS(status) != 0) {
			tst_resm(TFAIL, "child returned bad status");
			fail = 1;
		}
		if (fail)
			tst_resm(TFAIL, "%s FAILED", TCID);
		else
			tst_resm(TPASS, "%s PASSED", TCID);

		cleanup();
		tst_exit();
	} else if (pid < 0) {
		tst_brkm(TBROK, cleanup, "fork failed");
	}

	/*
	 * Set up to catch SIGINT.  The kids will wait till a SIGINT
	 * has been received before they proceed.
	 */
	setup_sigint();

	group1 = getpgrp();

	for (kid_count = 0; kid_count < MAXKIDS; kid_count++) {
		if (kid_count == (MAXKIDS / 2))
			group2 = setpgrp();

		intintr = 0;
		ret_val = FORK_OR_VFORK();
		if (ret_val == 0) {
#ifdef UCLINUX
			if (self_exec(av[0], "") < 0) {
				tst_resm(TFAIL | TERRNO, "self_exec kid %d "
					 "failed", kid_count);

			}
#else
			do_exit();
#endif
		}

		if (ret_val < 0)
			tst_resm(TFAIL | TERRNO, "forking kid %d failed",
				 kid_count);

		/* parent */
		fork_kid_pid[kid_count] = ret_val;
	}

	/* Check that waitpid with WNOHANG|WUNTRACED returns zero */
	ret_val = waitpid(0, &status, WNOHANG | WUNTRACED);
	if (ret_val != 0) {
		tst_resm(TFAIL, "Waitpid returned wrong value"
			 "from waitpid(WNOHANG|WUNTRACED)");
		tst_resm(TFAIL, "Expected 0 got %d", ret_val);
		fail = 1;
	}
#ifdef UCLINUX
	/* Give the kids a chance to setup SIGINT again, since this is
	 * cleared by exec().
	 */
	sleep(3);
#endif

	/* Now send all the kids a SIGINT to tell them to proceed */
	for (i = 0; i < MAXKIDS; i++) {
		if (kill(fork_kid_pid[i], SIGINT) < 0) {
			tst_resm(TFAIL | TERRNO, "killing child %d failed", i);
			fail = 1;
		}
	}

	/*
	 * Wait till all kids have terminated.  Stash away their
	 * pid's in an array.
	 */
	kid_count = 0;
	errno = 0;
	while (((ret_val = waitpid(0, &status, WUNTRACED)) != -1) ||
	       (errno == EINTR)) {
		if (ret_val == -1)
			continue;

		if (!WIFEXITED(status)) {
			if (!WIFSTOPPED(status)) {
				tst_resm(TFAIL, "Child %d is not "
					 "stopped", ret_val);
				fail = 1;
			} else {
				if (WSTOPSIG(status) != SIGSTOP) {
					tst_resm(TFAIL, "Child %d "
						 "exited with wrong "
						 "status", ret_val);
					tst_resm(TFAIL, "Expected "
						 "SIGSTOP got %d",
						 WEXITSTATUS(status));
					fail = 1;
				}
			}
			if (kill(ret_val, SIGCONT) < 0) {
				tst_resm(TFAIL | TERRNO,
					 "killing child %d failed", ret_val);
				fail = 1;
			}
		}
		found = 0;
		for (j = 0; j < kid_count; j++) {
			if (ret_val == wait_kid_pid[j]) {
				found = 1;
				break;
			}
		}
		if (!found)
			wait_kid_pid[kid_count++] = ret_val;
	}

	/*
	 * Check that for every entry in the fork_kid_pid array,
	 * there is a matching pid in the wait_kid_pid array.  If
	 * not, it's an error.
	 */
	for (i = 0; i < kid_count; i++) {
		found = 0;
		for (j = (MAXKIDS / 2); j < MAXKIDS; j++) {
			if (fork_kid_pid[j] == wait_kid_pid[i]) {
				found = 1;
				break;
			}
		}
		if (!found) {
			tst_resm(TFAIL, "Did not find a wait_kid_pid "
				 "for the fork_kid_pid of %d", wait_kid_pid[i]);
			for (k = 0; k < MAXKIDS; k++)
				tst_resm(TFAIL, "fork_kid_pid[%d] = "
					 "%d", k, fork_kid_pid[k]);
			for (k = 0; k < kid_count; k++)
				tst_resm(TFAIL, "wait_kid_pid[%d] = "
					 "%d", k, wait_kid_pid[k]);
			fail = 1;
		}
	}

	if (kid_count != (MAXKIDS / 2)) {
		tst_resm(TFAIL, "Wrong number of children waited on "
			 "for pid = 0");
		tst_resm(TFAIL, "Expected %d got %d", MAXKIDS, kid_count);
		fail = 1;
	}

	/* Make sure can pickup children in a diff. process group */

	kid_count = 0;
	errno = 0;
	while (((ret_val = waitpid(-(group1), &status, WUNTRACED)) !=
		-1) || (errno == EINTR)) {
		if (ret_val == -1)
			continue;
		if (!WIFEXITED(status)) {
			if (!WIFSTOPPED(status)) {
				tst_resm(TFAIL, "Child %d is not "
					 "stopped", ret_val);
				fail = 1;
			} else {
				if (WSTOPSIG(status) != SIGSTOP) {
					tst_resm(TFAIL, "Child %d "
						 "exited with wrong "
						 "status", ret_val);
					tst_resm(TFAIL, "Expected "
						 "SIGSTOP got %d",
						 WEXITSTATUS(status));
					fail = 1;
				}
			}
			if (kill(ret_val, SIGCONT) < 0) {
				tst_resm(TFAIL | TERRNO,
					 "Killing child %d failed", ret_val);
				fail = 1;
			}
		}
		found = 0;
		for (j = 0; j < kid_count; j++) {
			if (ret_val == wait_kid_pid[j]) {
				found = 1;
				break;
			}
		}
		if (!found)
			wait_kid_pid[kid_count++] = ret_val;
	}

	/*
	 * Check that for every entry in the fork_kid_pid array,
	 * there is a matching pid in the wait_kid_pid array.  If
	 * not, it's an error.
	 */
	for (i = 0; i < kid_count; i++) {
		found = 0;
		for (j = 0; j < (MAXKIDS / 2); j++) {
			if (fork_kid_pid[j] == wait_kid_pid[i]) {
				found = 1;
				break;
			}
		}
		if (!found) {
			tst_resm(TFAIL, "Did not find a wait_kid_pid "
				 "for the fork_kid_pid of %d", fork_kid_pid[j]);
			for (k = 0; k < MAXKIDS; k++)
				tst_resm(TFAIL, "fork_kid_pid[%d] = "
					 "%d", k, fork_kid_pid[k]);
			for (k = 0; k < kid_count; k++)
				tst_resm(TFAIL, "wait_kid_pid[%d] = "
					 "%d", k, wait_kid_pid[k]);
			fail = 1;
		}
	}
	if (kid_count != (MAXKIDS / 2)) {
		tst_resm(TFAIL, "Wrong number of children waited on "
			 "for pid = 0");
		tst_resm(TFAIL, "Expected %d got %d", MAXKIDS, kid_count);
		fail = 1;
	}

	/*
	 * Check that waitpid(WUNTRACED) returns -1 when no stopped
	 * children
	 */
	ret_val = waitpid(-1, &status, WUNTRACED);
	if (ret_val != -1) {
		tst_resm(TFAIL, "Waitpid returned wrong value.");
		tst_resm(TFAIL, "Expected -1 got %d", ret_val);
		fail = 1;
	}

	if (errno != ECHILD) {
		tst_resm(TFAIL, "Expected ECHILD from waitpid(WUNTRACED)");
		fail = 1;
	}

	if (fail)
		tst_resm(TFAIL, "Test FAILED");
	else
		tst_resm(TPASS, "Test PASSED");

	tst_exit();
}

static void setup_sigint(void)
{
	if (signal(SIGINT, inthandlr) == SIG_ERR)
		tst_brkm(TFAIL | TERRNO, NULL, "signal SIGINT failed");
}

static void setup(void)
{
	TEST_PAUSE;
}

static void cleanup(void)
{
}

static void inthandlr(void)
{
	intintr++;
}

static void wait_for_parent(void)
{
	int testvar;

	while (!intintr)
		testvar = 0;
}

static void do_exit(void)
{
	wait_for_parent();
	kill(getpid(), SIGSTOP);
	exit(3);
}

#ifdef UCLINUX
static void do_exit_uclinux(void)
{
	setup_sigint();
	do_exit();
}
#endif
