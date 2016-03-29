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
 * Test Name: alarm06
 *
 * Test Description:
 *  Check the functionality of the Alarm system call when the time input
 *  parameter is zero.
 *
 * Expected Result:
 *  The previously specified alarm request should be cancelled and the
 *  SIGALRM should not be received.
 *
 * Algorithm:
 *  Setup:
 *   Setup signal handling.
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
 *  Cleanup:
 *   Print errno log and/or timing stats if options given
 *
 * Usage:  <for command-line>
 *  alarm06 [-c n] [-f] [-i n] [-I x] [-P x] [-t]
 *     where,  -c n : Run n copies concurrently.
 *             -f   : Turn off functionality Testing.
 *	       -i n : Execute test n times.
 *	       -I x : Execute test for x seconds.
 *	       -P x : Pause for x seconds between iterations.
 *	       -t   : Turn on syscall timing.
 *
 * HISTORY
 *	07/2001 Ported by Wayne Boyer
 *
 * RESTRICTIONS:
 *  None.
 *
 */

#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>
#include <errno.h>
#include <string.h>
#include <signal.h>

#include "test.h"

char *TCID = "alarm06";
int TST_TOTAL = 1;
int alarms_received = 0;

void setup();
void cleanup();
void sigproc(int sig);

int main(int ac, char **av)
{
	int lc;
	int time_sec1 = 10;	/* time for which 1st alarm is set */
	int time_sec2 = 0;	/* time for which 2nd alarm is set */
	int ret_val1, ret_val2;	/* return values for alarm() calls */
	int sleep_time1 = 5;	/* waiting time for the 1st signal */
	int sleep_time2 = 10;	/* waiting time for the 2nd signal */

	tst_parse_opts(ac, av, NULL, NULL);

	setup();

	for (lc = 0; TEST_LOOPING(lc); lc++) {

		tst_count = 0;

		/*
		 * Call First alarm() with non-zero time parameter
		 * 'time_sec1' to send SIGALRM to the calling process.
		 */
		TEST(alarm(time_sec1));
		ret_val1 = TEST_RETURN;

		sleep(sleep_time1);

		TEST(alarm(time_sec2));
		ret_val2 = TEST_RETURN;

		/* Wait for signal SIGALRM */
		sleep(sleep_time2);

		/*
		 * Check whether the second alarm() call returned
		 * the amount of time (seconds) previously remaining in the
		 * alarm clock of the calling process, and
		 * sigproc() never executed as SIGALRM was not received by the
		 * process, the variable alarms_received remains unset.
		 */
		if ((alarms_received == 0) &&
		    (ret_val2 == (time_sec1 - sleep_time1)))
			tst_resm(TPASS, "Functionality of alarm(%u) "
				 "successful", time_sec2);
		else
			tst_resm(TFAIL, "alarm(%u) fails, returned %d, "
				 "alarms_received:%d",
				 time_sec2, ret_val2, alarms_received);
	}

	cleanup();
	tst_exit();
}

void setup(void)
{

	tst_sig(NOFORK, DEF_HANDLER, cleanup);

	TEST_PAUSE;

	/* Set the signal catching function */
	if (signal(SIGALRM, sigproc) == SIG_ERR)
		tst_brkm(TFAIL | TERRNO, cleanup, "signal(SIGALRM, ..) failed");
}

void sigproc(int sig)
{
	alarms_received++;
}

void cleanup(void)
{
}
