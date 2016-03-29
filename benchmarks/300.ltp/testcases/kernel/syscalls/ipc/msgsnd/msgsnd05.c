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
 *	msgsnd05.c
 *
 * DESCRIPTION
 *	msgsnd05 - test for EINTR error
 *
 * ALGORITHM
 *	create a message queue with read/write permissions
 *	initialize a message buffer with a known message and type
 *	enqueue the message in a loop until the queue is full
 *	loop if that option was specified
 *	fork a child process
 *	child attempts to enqueue a message to the full queue and sleeps
 *	parent sends a SIGHUP to the child then waits for the child to complete
 *	child get a return from msgsnd()
 *	check the errno value
 *	  issue a PASS message if we get EINTR
 *	otherwise, the tests fails
 *	  issue a FAIL message
 *	child exits, parent calls cleanup
 *
 * USAGE:  <for command-line>
 *  msgsnd05 [-c n] [-e] [-i n] [-I x] [-P x] [-t]
 *     where,  -c n : Run n copies concurrently.
 *             -e   : Turn on errno logging.
 *	       -i n : Execute test n times.
 *	       -I x : Execute test for x seconds.
 *	       -P x : Pause for x seconds between iterations.
 *	       -t   : Turn on syscall timing.
 *
 * HISTORY
 *	03/2001 - Written by Wayne Boyer
 *      14/03/2008 Matthieu Fertré (Matthieu.Fertre@irisa.fr)
 *      - Fix concurrency issue. Due to the use of usleep function to
 *        synchronize processes, synchronization issues can occur on a loaded
 *        system. Fix this by using pipes to synchronize processes.
 *
 * RESTRICTIONS
 *	none
 */

#include "test.h"

#include "ipcmsg.h"

#include <sys/types.h>
#include <sys/wait.h>

void do_child(void);
void cleanup(void);
void setup(void);
#ifdef UCLINUX
#define PIPE_NAME	"msgsnd05"
void do_child_uclinux(void);
#endif

char *TCID = "msgsnd05";
int TST_TOTAL = 1;

int msg_q_1 = -1;		/* The message queue id created in setup */

MSGBUF msg_buf;

int main(int ac, char **av)
{
	int lc;
	pid_t c_pid;

	tst_parse_opts(ac, av, NULL, NULL);

#ifdef UCLINUX
	maybe_run_child(&do_child_uclinux, "d", &msg_q_1);
#endif

	setup();		/* global setup */

	/* The following loop checks looping state if -i option given */

	for (lc = 0; TEST_LOOPING(lc); lc++) {
		/* reset tst_count in case we are looping */
		tst_count = 0;

		/*
		 * fork a child that will attempt to write a message
		 * to the queue without IPC_NOWAIT
		 */
		if ((c_pid = FORK_OR_VFORK()) == -1) {
			tst_brkm(TBROK, cleanup, "could not fork");
		}

		if (c_pid == 0) {	/* child */
			/*
			 * Attempt to write another message to the full queue.
			 * Without the IPC_NOWAIT flag, the child sleeps
			 */

#ifdef UCLINUX
			if (self_exec(av[0], "d", msg_q_1) < 0) {
				tst_brkm(TBROK, cleanup, "could not self_exec");
			}
#else
			do_child();
#endif
		} else {
			TST_PROCESS_STATE_WAIT(cleanup, c_pid, 'S');

			/* send a signal that must be caught to the child */
			if (kill(c_pid, SIGHUP) == -1)
				tst_brkm(TBROK, cleanup, "kill failed");

			waitpid(c_pid, NULL, 0);
		}
	}

	cleanup();

	tst_exit();
}

/*
 * do_child()
 */
void do_child(void)
{
	TEST(msgsnd(msg_q_1, &msg_buf, MSGSIZE, 0));

	if (TEST_RETURN != -1) {
		tst_resm(TFAIL, "call succeeded when error expected");
		exit(-1);
	}

	switch (TEST_ERRNO) {
	case EINTR:
		tst_resm(TPASS, "expected failure - errno = %d : %s",
			 TEST_ERRNO, strerror(TEST_ERRNO));
		break;
	default:
		tst_resm(TFAIL,
			 "call failed with an unexpected error - %d : %s",
			 TEST_ERRNO, strerror(TEST_ERRNO));
		break;
	}

	exit(0);
}

void sighandler(int sig)
{
	if (sig == SIGHUP)
		return;
	else
		tst_brkm(TBROK, NULL, "received unexpected signal %d", sig);
}

#ifdef UCLINUX
/*
 * do_child_uclinux() - capture signals, initialize buffer, then run do_child()
 */
void do_child_uclinux(void)
{
	/* initialize the message buffer */
	init_buf(&msg_buf, MSGTYPE, MSGSIZE);

	tst_sig(FORK, sighandler, cleanup);

	do_child();
}
#endif

/*
 * setup() - performs all the ONE TIME setup for this test.
 */
void setup(void)
{
	/* capture signals in our own handler */
	tst_sig(FORK, sighandler, cleanup);

	TEST_PAUSE;

	/*
	 * Create a temporary directory and cd into it.
	 * This helps to ensure that a unique msgkey is created.
	 * See ../lib/libipc.c for more information.
	 */
	tst_tmpdir();

	msgkey = getipckey();

	/* create a message queue with read/write permission */
	if ((msg_q_1 = msgget(msgkey, IPC_CREAT | IPC_EXCL | MSG_RW)) == -1) {
		tst_brkm(TBROK, cleanup, "Can't create message queue");
	}

	/* initialize the message buffer */
	init_buf(&msg_buf, MSGTYPE, MSGSIZE);

	/* write messages to the queue until it is full */
	while (msgsnd(msg_q_1, &msg_buf, MSGSIZE, IPC_NOWAIT) != -1) {
		msg_buf.mtype += 1;
	}
}

/*
 * cleanup() - performs all the ONE TIME cleanup for this test at completion
 * 	       or premature exit.
 */
void cleanup(void)
{
	/* if it exists, remove the message queue that was created */
	rm_queue(msg_q_1);

	tst_rmdir();

}
