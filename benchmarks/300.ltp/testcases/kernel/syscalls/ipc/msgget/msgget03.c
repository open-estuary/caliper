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
 *	msgget03.c
 *
 * DESCRIPTION
 *	msgget03 - test for an ENOSPC error by using up all available
 *		   message queues.
 *
 * ALGORITHM
 *	Get all the message queues that can be allocated
 *	loop if that option was specified
 *	Try to get one more message queue
 *	check the errno value
 *	  issue a PASS message if we get ENOSPC
 *	otherwise, the tests fails
 *	  issue a FAIL message
 *	  break any remaining tests
 *	  call cleanup
 *
 * USAGE:  <for command-line>
 *  msgget03 [-c n] [-e] [-i n] [-I x] [-P x] [-t]
 *     where,  -c n : Run n copies concurrently.
 *             -e   : Turn on errno logging.
 *	       -i n : Execute test n times.
 *	       -I x : Execute test for x seconds.
 *	       -P x : Pause for x seconds between iterations.
 *	       -t   : Turn on syscall timing.
 *
 * HISTORY
 *	03/2001 - Written by Wayne Boyer
 *
 * RESTRICTIONS
 *	none
 */

#include "test.h"

#include "ipcmsg.h"

char *TCID = "msgget03";
int TST_TOTAL = 1;

int maxmsgs = 0;

int *msg_q_arr = NULL;		/* hold the id's that we create */
int num_queue = 0;		/* count the queues created */

int main(int ac, char **av)
{
	int lc;
	int msg_q;

	tst_parse_opts(ac, av, NULL, NULL);

	setup();		/* global setup */

	/* The following loop checks looping state if -i option given */

	for (lc = 0; TEST_LOOPING(lc); lc++) {
		/* reset tst_count in case we are looping */
		tst_count = 0;

		/*
		 * Use a while loop to create the maximum number of queues.
		 * When we get an error, check for ENOSPC.
		 */
		while ((msg_q =
			msgget(msgkey + num_queue,
			       IPC_CREAT | IPC_EXCL)) != -1) {
			msg_q_arr[num_queue] = msg_q;
			if (num_queue == maxmsgs) {
				tst_resm(TINFO, "The maximum number of message"
					 " queues (%d) has been reached",
					 maxmsgs);
				break;
			}
			num_queue++;
		}

		switch (errno) {
		case ENOSPC:
			tst_resm(TPASS, "expected failure - errno = %d : %s",
				 TEST_ERRNO, strerror(TEST_ERRNO));
			break;
		default:
			tst_resm(TFAIL, "call failed with an "
				 "unexpected error - %d : %s",
				 TEST_ERRNO, strerror(TEST_ERRNO));
			break;
		}
	}

	cleanup();

	tst_exit();
}

/*
 * setup() - performs all the ONE TIME setup for this test.
 */
void setup(void)
{

	tst_sig(NOFORK, DEF_HANDLER, cleanup);

	TEST_PAUSE;

	/*
	 * Create a temporary directory and cd into it.
	 * This helps to ensure that a unique msgkey is created.
	 * See ../lib/libipc.c for more information.
	 */
	tst_tmpdir();

	msgkey = getipckey();

	maxmsgs = get_max_msgqueues();
	if (maxmsgs < 0)
		tst_brkm(TBROK, cleanup, "get_max_msgqueues failed");

	msg_q_arr = (int *)calloc(maxmsgs, sizeof(int));
	if (msg_q_arr == NULL) {
		tst_brkm(TBROK, cleanup, "Couldn't allocate memory "
			 "for msg_q_arr: calloc() failed");
	}
}

/*
 * cleanup() - performs all the ONE TIME cleanup for this test at completion
 * 	       or premature exit.
 */
void cleanup(void)
{
	int i;

	/*
	 * remove the message queues if they were created
	 */

	if (msg_q_arr != NULL) {
		for (i = 0; i < num_queue; i++) {
			rm_queue(msg_q_arr[i]);
		}
		(void)free(msg_q_arr);
	}

	tst_rmdir();

}
