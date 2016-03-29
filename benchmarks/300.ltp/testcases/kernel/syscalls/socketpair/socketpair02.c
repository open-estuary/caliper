/******************************************************************************/
/*                                                                            */
/* Copyright (c) Ulrich Drepper <drepper@redhat.com>                          */
/* Copyright (c) International Business Machines  Corp., 2009                 */
/*                                                                            */
/* This program is free software;  you can redistribute it and/or modify      */
/* it under the terms of the GNU General Public License as published by       */
/* the Free Software Foundation; either version 2 of the License, or          */
/* (at your option) any later version.                                        */
/*                                                                            */
/* This program is distributed in the hope that it will be useful,            */
/* but WITHOUT ANY WARRANTY;  without even the implied warranty of            */
/* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See                  */
/* the GNU General Public License for more details.                           */
/*                                                                            */
/* You should have received a copy of the GNU General Public License          */
/* along with this program;  if not, write to the Free Software               */
/* Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA    */
/*                                                                            */
/******************************************************************************/
/******************************************************************************/
/*                                                                            */
/* File:        socketpair02.c                                                */
/*                                                                            */
/* Description: This Program tests the new system call introduced in 2.6.27.  */
/*              Ulrich´s comment as in:                                       */
/* http://git.kernel.org/?p=linux/kernel/git/torvalds/linux-2.6.git;a=commit;h=77d2720059618b9b6e827a8b73831eb6c6fad63c */
/*                                                                            */
/* Usage:  <for command-line>                                                 */
/* socketpair02 [-c n] [-e][-i n] [-I x] [-p x] [-t]                          */
/*      where,  -c n : Run n copies concurrently.                             */
/*              -e   : Turn on errno logging.                                 */
/*              -i n : Execute test n times.                                  */
/*              -I x : Execute test for x seconds.                            */
/*              -P x : Pause for x seconds between iterations.                */
/*              -t   : Turn on syscall timing.                                */
/*                                                                            */
/* Total Tests: 1                                                             */
/*                                                                            */
/* Test Name:   socketpair02                                                  */
/*                                                                            */
/* Author:      Ulrich Drepper <drepper@redhat.com>                           */
/*                                                                            */
/* History:     Created - Jan 13 2009 - Ulrich Drepper <drepper@redhat.com>   */
/*              Ported to LTP                                                 */
/*                      - Jan 13 2009 - Subrata <subrata@linux.vnet.ibm.com>  */
/******************************************************************************/
#include <fcntl.h>
#include <pthread.h>
#include <stdio.h>
#include <unistd.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <sys/syscall.h>

#include "test.h"

#ifndef SOCK_NONBLOCK
#define SOCK_NONBLOCK O_NONBLOCK
#endif

int TST_TOTAL = 2;
char *TCID = "socketpair02";

/* Extern Global Functions */
/******************************************************************************/
/*                                                                            */
/* Function:    cleanup                                                       */
/*                                                                            */
/* Description: Performs all one time clean up for this test on successful    */
/*              completion,  premature exit or  failure. Closes all temporary */
/*              files, removes all temporary directories exits the test with  */
/*              appropriate return code by calling tst_exit() function.       */
/*                                                                            */
/* Input:       None.                                                         */
/*                                                                            */
/* Output:      None.                                                         */
/*                                                                            */
/* Return:      On failure - Exits calling tst_exit(). Non '0' return code.   */
/*              On success - Exits calling tst_exit(). With '0' return code.  */
/*                                                                            */
/******************************************************************************/
void cleanup(void)
{

	tst_rmdir();
}

/* Local  Functions */
/******************************************************************************/
/*                                                                            */
/* Function:    setup                                                         */
/*                                                                            */
/* Description: Performs all one time setup for this test. This function is   */
/*              typically used to capture signals, create temporary dirs      */
/*              and temporary files that may be used in the course of this    */
/*              test.                                                         */
/*                                                                            */
/* Input:       None.                                                         */
/*                                                                            */
/* Output:      None.                                                         */
/*                                                                            */
/* Return:      On failure - Exits by calling cleanup().                      */
/*              On success - returns 0.                                       */
/*                                                                            */
/******************************************************************************/
void setup(void)
{
	/* Capture signals if any */
	/* Create temporary directories */
	TEST_PAUSE;
	tst_tmpdir();
}

int main(int argc, char *argv[])
{
	int fds[2], fl, i;

	if ((tst_kvercmp(2, 6, 27)) < 0) {
		tst_brkm(TCONF, NULL,
			 "This test can only run on kernels that are 2.6.27 and higher");
	}
	setup();

	if (socketpair(PF_UNIX, SOCK_STREAM, 0, fds) == -1) {
		tst_brkm(TFAIL, cleanup, "socketpair(0) failed");
	}
	for (i = 0; i < ARRAY_SIZE(fds); i++) {
		fl = fcntl(fds[i], F_GETFL);
		if (fl == -1) {
			tst_brkm(TBROK, cleanup, "fcntl failed");
		}
		if (fl & O_NONBLOCK) {
			tst_brkm(TFAIL, cleanup,
				 "socketpair(0) set non-blocking mode for fds[%d]",
				 i);
		}
		close(fds[i]);
	}

	if (socketpair(PF_UNIX, SOCK_STREAM | SOCK_NONBLOCK, 0, fds) == -1) {
		tst_brkm(TFAIL, cleanup, "socketpair(SOCK_NONBLOCK) failed");
	}
	for (i = 0; i < ARRAY_SIZE(fds); i++) {
		fl = fcntl(fds[i], F_GETFL);
		if (fl == -1) {
			tst_brkm(TBROK, cleanup, "fcntl failed");
		}
		if ((fl & O_NONBLOCK) == 0) {
			tst_brkm(TFAIL, cleanup,
				 "socketpair(SOCK_NONBLOCK) didn't set non-blocking "
				 "mode for fds[%d]", i);
		}
		close(fds[i]);
	}
	tst_resm(TPASS, "socketpair(SOCK_NONBLOCK) PASSED");
	cleanup();
	tst_exit();
}
