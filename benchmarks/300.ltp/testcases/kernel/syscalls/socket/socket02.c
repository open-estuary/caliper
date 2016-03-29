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
/* File:        socket02.c                                                    */
/*                                                                            */
/* Description: This program tests the new flag SOCK_CLOEXEC introduced in    */
/*              socket() & socketpair() and in kernel 2.6.27. Ulrich´s comment*/
/*              as in:                                                        */
/*              http://git.kernel.org/?p=linux/kernel/git/torvalds/linux-2.6.git;a=commit;h=a677a039be7243357d93502bff2b40850c942e2d */
/*              says:                                                         */
/*                                                                            */
/*              flag parameters: socket and socketpair                        */
/*              This patch adds support for flag values which are ORed to the */
/*              type passwd to socket and socketpair.  The additional code is */
/*              minimal. The flag values in this implementation can and must  */
/*              match the O_* flags. This avoids overhead in the conversion.  */
/*              The internal functions sock_alloc_fd and sock_map_fd get a new*/
/*              parameters and all callers are changed.                       */
/*                                                                            */
/* Usage:  <for command-line>                                                 */
/*  socket02 [-c n] [-e][-i n] [-I x] [-p x] [-t]                             */
/*      where,  -c n : Run n copies concurrently.                             */
/*              -e   : Turn on errno logging.                                 */
/*              -i n : Execute test n times.                                  */
/*              -I x : Execute test for x seconds.                            */
/*              -P x : Pause for x seconds between iterations.                */
/*              -t   : Turn on syscall timing.                                */
/*                                                                            */
/* Total Tests: 1                                                             */
/*                                                                            */
/* Test Name:   socket02                                                      */
/*                                                                            */
/* Author:      Ulrich Drepper <drepper@redhat.com>                           */
/*                                                                            */
/* History:     Created - Jan 05 2009 - Ulrich Drepper <drepper@redhat.com>   */
/*              Ported to LTP                                                 */
/*                      - Jan 05 2009 - Subrata <subrata@linux.vnet.ibm.com>  */
/******************************************************************************/

#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>
#include <netinet/in.h>
#include <sys/socket.h>

#include "test.h"
#include "lapi/fcntl.h"

#define PORT 57392

/* For Linux these must be the same.  */
#ifndef SOCK_CLOEXEC
#define SOCK_CLOEXEC O_CLOEXEC
#endif

char *TCID = "socket02";
int testno;
int TST_TOTAL = 1;

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
	int fd, fds[2], i, coe;
	int lc;

	tst_parse_opts(argc, argv, NULL, NULL);
	if ((tst_kvercmp(2, 6, 27)) < 0) {
		tst_brkm(TCONF,
			 NULL,
			 "This test can only run on kernels that are 2.6.27 and higher");
	}
	setup();

	for (lc = 0; TEST_LOOPING(lc); ++lc) {
		tst_count = 0;
		for (testno = 0; testno < TST_TOTAL; ++testno) {
			fd = socket(PF_INET, SOCK_STREAM, 0);
			if (fd == -1) {
				tst_brkm(TBROK, cleanup, "socket(0) failed");
			}
			coe = fcntl(fd, F_GETFD);
			if (coe == -1) {
				tst_brkm(TBROK, cleanup, "fcntl failed");
			}
			if (coe & FD_CLOEXEC) {
				tst_brkm(TFAIL,
					 cleanup,
					 "socket(0) set close-on-exec flag");
			}
			close(fd);

			fd = socket(PF_INET, SOCK_STREAM | SOCK_CLOEXEC, 0);
			if (fd == -1) {
				tst_brkm(TFAIL, cleanup,
					 "socket(SOCK_CLOEXEC) failed");
			}
			coe = fcntl(fd, F_GETFD);
			if (coe == -1) {
				tst_brkm(TBROK, cleanup, "fcntl failed");
			}
			if ((coe & FD_CLOEXEC) == 0) {
				tst_brkm(TFAIL,
					 cleanup,
					 "socket(SOCK_CLOEXEC) does not set close-on-exec flag");
			}
			close(fd);

			if (socketpair(PF_UNIX, SOCK_STREAM, 0, fds) == -1) {
				tst_brkm(TBROK, cleanup,
					 "socketpair(0) failed");
			}
			for (i = 0; i < 2; ++i) {
				coe = fcntl(fds[i], F_GETFD);
				if (coe == -1) {
					tst_brkm(TBROK, cleanup,
						 "fcntl failed");
				}
				if (coe & FD_CLOEXEC) {
					tst_brkm(TFAIL,
						 cleanup, "socketpair(0) set close-on-exec flag for fds[%d]\n",
						 i);
				}
				close(fds[i]);
			}

			if (socketpair
			    (PF_UNIX, SOCK_STREAM | SOCK_CLOEXEC, 0,
			     fds) == -1) {
				tst_brkm(TBROK, cleanup,
					 "socketpair(SOCK_CLOEXEC) failed");
			}
			for (i = 0; i < 2; ++i) {
				coe = fcntl(fds[i], F_GETFD);
				if (coe == -1) {
					tst_brkm(TBROK, cleanup,
						 "fcntl failed");
				}
				if ((coe & FD_CLOEXEC) == 0) {
					tst_brkm(TFAIL,
						 cleanup, "socketpair(SOCK_CLOEXEC) does not set close-on-exec flag for fds[%d]\n",
						 i);
				}
				close(fds[i]);
			}
			tst_resm(TPASS, "socket(SOCK_CLOEXEC) PASSED");
			cleanup();
		}
	}
	tst_exit();
}
