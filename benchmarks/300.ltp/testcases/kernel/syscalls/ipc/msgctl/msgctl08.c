/*
 * Copyright (c) International Business Machines  Corp., 2002
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
 *
 * 06/30/2001   Port to Linux   nsharoff@us.ibm.com
 * 11/06/2002   Port to LTP     dbarrera@us.ibm.com
 */

/*
 * Get and manipulate a message queue.
 */

#define _XOPEN_SOURCE 500
#include <signal.h>
#include <errno.h>
#include <string.h>
#include <fcntl.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <values.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/stat.h>
#include <sys/ipc.h>
#include <sys/msg.h>
#include "test.h"
#include "ipcmsg.h"
#include "../lib/libmsgctl.h"

char *TCID = "msgctl08";
int TST_TOTAL = 1;

#ifndef CONFIG_COLDFIRE
#define MAXNPROCS	1000000	/* This value is set to an arbitrary high limit. */
#else
#define MAXNPROCS	 100000	/* Coldfire can't deal with 1000000 */
#endif
#define MAXNREPS	100000

static key_t keyarray[MAXNPROCS];
static int pidarray[MAXNPROCS];
static int tid;
static int MSGMNI, nprocs, nreps;
static int procstat;
static int mykid;

void setup(void);
void cleanup(void);

static int dotest(key_t key, int child_process);
static void sig_handler();

#ifdef UCLINUX
static char *argv0;
static key_t key_uclinux;
static int i_uclinux;
static int id_uclinux;
static int child_process_uclinux;

static void do_child_1_uclinux(void);
static void do_child_2_uclinux(void);
#endif

int main(int argc, char **argv)
{
	int i, j, ok, pid;
	int count, status;
	struct sigaction act;

#ifdef UCLINUX

	argv0 = argv[0];

	tst_parse_opts(argc, argv, NULL, NULL);

	maybe_run_child(&do_child_1_uclinux, "ndd", 1, &key_uclinux,
			&i_uclinux);
	maybe_run_child(&do_child_2_uclinux, "nddd", 2, &id_uclinux,
			&key_uclinux, &child_process_uclinux);
#endif

	setup();

	if (argc == 1) {
		/* Set default parameters */
		nreps = MAXNREPS;
		nprocs = MSGMNI;
	} else if (argc == 3) {
		if (atoi(argv[1]) > MAXNREPS) {
			tst_resm(TCONF,
				 "Requested number of iterations too large, setting to Max. of %d",
				 MAXNREPS);
			nreps = MAXNREPS;
		} else {
			nreps = atoi(argv[1]);
		}
		if (atoi(argv[2]) > MSGMNI) {
			tst_resm(TCONF,
				 "Requested number of processes too large, setting to Max. of %d",
				 MSGMNI);
			nprocs = MSGMNI;
		} else {
			nprocs = atoi(argv[2]);
		}
	} else {
		tst_brkm(TCONF,
			 NULL,
			 " Usage: %s [ number of iterations  number of processes ]",
			 argv[0]);
	}

	srand(getpid());
	tid = -1;

	/* Setup signal handling routine */
	memset(&act, 0, sizeof(act));
	act.sa_handler = sig_handler;
	sigemptyset(&act.sa_mask);
	sigaddset(&act.sa_mask, SIGTERM);
	if (sigaction(SIGTERM, &act, NULL) < 0) {
		tst_brkm(TFAIL, NULL, "Sigset SIGTERM failed");
	}
	/* Set up array of unique keys for use in allocating message
	 * queues
	 */
	for (i = 0; i < nprocs; i++) {
		ok = 1;
		do {
			/* Get random key */
			keyarray[i] = (key_t) rand();
			/* Make sure key is unique and not private */
			if (keyarray[i] == IPC_PRIVATE) {
				ok = 0;
				continue;
			}
			for (j = 0; j < i; j++) {
				if (keyarray[j] == keyarray[i]) {
					ok = 0;
					break;
				}
				ok = 1;
			}
		} while (ok == 0);
	}

	/* Fork a number of processes, each of which will
	 * create a message queue with one reader/writer
	 * pair which will read and write a number (iterations)
	 * of random length messages with specific values.
	 */

	for (i = 0; i < nprocs; i++) {
		fflush(stdout);
		if ((pid = FORK_OR_VFORK()) < 0) {
			tst_brkm(TFAIL,
				 NULL,
				 "\tFork failed (may be OK if under stress)");
		}
		/* Child does this */
		if (pid == 0) {
#ifdef UCLINUX
			if (self_exec(argv[0], "ndd", 1, keyarray[i], i) < 0) {
				tst_brkm(TFAIL, NULL, "\tself_exec failed");
			}
#else
			procstat = 1;
			exit(dotest(keyarray[i], i));
#endif
		}
		pidarray[i] = pid;
	}

	count = 0;
	while (1) {
		if ((wait(&status)) > 0) {
			if (status >> 8 != 0) {
				tst_brkm(TFAIL, NULL,
					 "Child exit status = %d",
					 status >> 8);
			}
			count++;
		} else {
			if (errno != EINTR) {
				break;
			}
#ifdef DEBUG
			tst_resm(TINFO, "Signal detected during wait");
#endif
		}
	}
	/* Make sure proper number of children exited */
	if (count != nprocs) {
		tst_brkm(TFAIL,
			 NULL,
			 "Wrong number of children exited, Saw %d, Expected %d",
			 count, nprocs);
	}

	tst_resm(TPASS, "msgctl08 ran successfully!");

	cleanup();
	tst_exit();
}

#ifdef UCLINUX
static void do_child_1_uclinux(void)
{
	procstat = 1;
	exit(dotest(key_uclinux, i_uclinux));
}

static void do_child_2_uclinux(void)
{
	exit(doreader(key_uclinux, id_uclinux, 1,
			child_process_uclinux, nreps));
}
#endif

static int dotest(key_t key, int child_process)
{
	int id, pid;
	int ret, status;

	sighold(SIGTERM);
	TEST(msgget(key, IPC_CREAT | S_IRUSR | S_IWUSR));
	if (TEST_RETURN < 0) {
		printf("msgget() error in child %d: %s\n",
			child_process, strerror(TEST_ERRNO));

		return FAIL;
	}
	tid = id = TEST_RETURN;
	sigrelse(SIGTERM);

	fflush(stdout);
	if ((pid = FORK_OR_VFORK()) < 0) {
		printf("\tFork failed (may be OK if under stress)\n");
		TEST(msgctl(tid, IPC_RMID, 0));
		if (TEST_RETURN < 0) {
			printf("mscgtl() error in cleanup: %s\n",
				strerror(TEST_ERRNO));
		}
		return FAIL;
	}
	/* Child does this */
	if (pid == 0) {
#ifdef UCLINUX
		if (self_exec(argv0, "nddd", 2, id, key, child_process) < 0) {
			printf("self_exec failed\n");
			TEST(msgctl(tid, IPC_RMID, 0));
			if (TEST_RETURN < 0) {
				printf("msgctl() error in cleanup: %s\n",
					strerror(errno));
			}
			return FAIL;
		}
#else
		exit(doreader(key, id, 1, child_process, nreps));
#endif
	}
	/* Parent does this */
	mykid = pid;
	procstat = 2;
	ret = dowriter(key, id, 1, child_process, nreps);
	wait(&status);

	if (ret != PASS)
		exit(FAIL);

	if ((!WIFEXITED(status) || (WEXITSTATUS(status) != PASS)))
		exit(FAIL);

	TEST(msgctl(id, IPC_RMID, 0));
	if (TEST_RETURN < 0) {
		printf("msgctl() errno %d: %s\n",
			TEST_ERRNO, strerror(TEST_ERRNO));

		return FAIL;
	}
	return PASS;
}

static void sig_handler(void)
{
}

void setup(void)
{
	int nr_msgqs;

	tst_tmpdir();

	tst_sig(FORK, DEF_HANDLER, cleanup);

	TEST_PAUSE;

	nr_msgqs = get_max_msgqueues();
	if (nr_msgqs < 0)
		cleanup();

	nr_msgqs -= get_used_msgqueues();
	if (nr_msgqs <= 0) {
		tst_resm(TBROK,
			 "Max number of message queues already used, cannot create more.");
		cleanup();
	}

	/*
	 * Since msgmni scales to the memory size, it may reach huge values
	 * that are not necessary for this test.
	 * That's why we define NR_MSGQUEUES as a high boundary for it.
	 */
	MSGMNI = min(nr_msgqs, NR_MSGQUEUES);
}

void cleanup(void)
{
	int status;

#ifdef DEBUG
	tst_resm(TINFO, "Removing the message queue");
#endif
	fflush(stdout);
	(void)msgctl(tid, IPC_RMID, NULL);
	if ((status = msgctl(tid, IPC_STAT, NULL)) != -1) {
		(void)msgctl(tid, IPC_RMID, NULL);
		tst_resm(TFAIL, "msgctl(tid, IPC_RMID) failed");

	}

	fflush(stdout);

	tst_rmdir();
}
