/******************************************************************************/
/* Copyright (c) Crackerjack Project., 2007-2008 ,Hitachi, Ltd		      */
/*	  Author(s): Takahiro Yasui <takahiro.yasui.mp@hitachi.com>,	      */
/*		       Yumiko Sugita <yumiko.sugita.yf@hitachi.com>,          */
/*		       Satoshi Fujiwara <sa-fuji@sdl.hitachi.co.jp>	      */
/* Porting from Crackerjack to LTP is done by		                      */
/*         Manas Kumar Nayak maknayak@in.ibm.com>			      */
/*								              */
/* This program is free software;  you can redistribute it and/or modify      */
/* it under the terms of the GNU General Public License as published by       */
/* the Free Software Foundation; either version 2 of the License, or	      */
/* (at your option) any later version.					      */
/*									      */
/* This program is distributed in the hope that it will be useful,	      */
/* but WITHOUT ANY WARRANTY;  without even the implied warranty of	      */
/* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See		      */
/* the GNU General Public License for more details.			      */
/*									      */
/* You should have received a copy of the GNU General Public License	      */
/* along with this program;  if not, write to the Free Software Foundation,   */
/* Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA           */
/*									      */
/******************************************************************************/
/******************************************************************************/
/*									      */
/* Description: This tests the mq_notify() syscall			      */
/*									      */
/******************************************************************************/
#define _XOPEN_SOURCE 600
#include <sys/syscall.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/uio.h>
#include <getopt.h>
#include <libgen.h>
#include <limits.h>
#include <errno.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <mqueue.h>
#include <signal.h>
#include <stdlib.h>

#include "../utils/include_j_h.h"

#include "test.h"
#include "linux_syscall_numbers.h"

char *TCID = "mq_notify01";
int testno;
int TST_TOTAL = 1;

static void cleanup(void)
{
	tst_rmdir();
}

static void setup(void)
{
	TEST_PAUSE;
	tst_tmpdir();
}

#define SYSCALL_NAME    "mq_notify"

static int opt_debug;
static char *progname;
static int notified;
static int cmp_ok;

enum test_type {
	NORMAL,
	FD_NONE,
	FD_NOT_EXIST,
	FD_FILE,
	ALREADY_REGISTERED,
};

struct test_case {
	int notify;
	int ttype;
	int ret;
	int err;
};

#define MAX_MSGSIZE     8192
#define MSG_SIZE	16
#define USER_DATA       0x12345678

static struct test_case tcase[] = {
	{			// case00
	 .ttype = NORMAL,
	 .notify = SIGEV_NONE,
	 .ret = 0,
	 .err = 0,
	 },
	{			// case01
	 .ttype = NORMAL,
	 .notify = SIGEV_SIGNAL,
	 .ret = 0,
	 .err = 0,
	 },
	{			// case02
	 .ttype = NORMAL,
	 .notify = SIGEV_THREAD,
	 .ret = 0,
	 .err = 0,
	 },
	{			// case03
	 .ttype = FD_NONE,
	 .notify = SIGEV_NONE,
	 .ret = -1,
	 .err = EBADF,
	 },
	{			// case04
	 .ttype = FD_NOT_EXIST,
	 .notify = SIGEV_NONE,
	 .ret = -1,
	 .err = EBADF,
	 },
	{			// case05
	 .ttype = FD_FILE,
	 .notify = SIGEV_NONE,
	 .ret = -1,
	 .err = EBADF,
	 },
	{			// case06
	 .ttype = ALREADY_REGISTERED,
	 .notify = SIGEV_NONE,
	 .ret = -1,
	 .err = EBUSY,
	 },
};

static void sigfunc(int signo, siginfo_t * info, void *data)
{
	if (opt_debug) {
		tst_resm(TINFO, "si_code  E:%d,\tR:%d", info->si_code,
			 SI_MESGQ);
		tst_resm(TINFO, "si_signo E:%d,\tR:%d", info->si_signo,
			 SIGUSR1);
		tst_resm(TINFO, "si_value E:0x%x,\tR:0x%x",
			 info->si_value.sival_int, USER_DATA);
		tst_resm(TINFO, "si_pid   E:%d,\tR:%d", info->si_pid, getpid());
		tst_resm(TINFO, "si_uid   E:%d,\tR:%d", info->si_uid, getuid());
	}
	cmp_ok = info->si_code == SI_MESGQ &&
	    info->si_signo == SIGUSR1 &&
	    info->si_value.sival_int == USER_DATA &&
	    info->si_pid == getpid() && info->si_uid == getuid();
	notified = 1;
}

static void tfunc(union sigval sv)
{
	cmp_ok = sv.sival_int == USER_DATA;
	notified = 1;
}

static int do_test(struct test_case *tc)
{
	int sys_ret;
	int sys_errno;
	int result = RESULT_OK;
	int rc, i, fd = -1;
	struct sigevent ev;
	struct sigaction sigact;
	struct timespec abs_timeout;
	char smsg[MAX_MSGSIZE];

	notified = cmp_ok = 1;

	/* Don't timeout. */
	abs_timeout.tv_sec = 0;
	abs_timeout.tv_nsec = 0;

	/*
	 * When test ended with SIGTERM etc, mq discriptor is left remains.
	 * So we delete it first.
	 */
	mq_unlink(QUEUE_NAME);

	switch (tc->ttype) {
	case FD_NOT_EXIST:
		fd = INT_MAX - 1;
		/* fallthrough */
	case FD_NONE:
		break;
	case FD_FILE:
		TEST(fd = open("/", O_RDONLY));
		if (TEST_RETURN < 0) {
			tst_resm(TFAIL, "can't open \"/\".");
			result = 1;
			goto EXIT;
		}
		break;
	default:
		/*
		 * Open message queue
		 */
		TEST(fd =
		     mq_open(QUEUE_NAME, O_CREAT | O_EXCL | O_RDWR, S_IRWXU,
			     NULL));
		if (TEST_RETURN < 0) {
			tst_resm(TFAIL | TTERRNO, "mq_open failed");
			result = 1;
			goto EXIT;
		}
	}

	/*
	 * Set up struct sigevent
	 */
	ev.sigev_notify = tc->notify;

	switch (tc->notify) {
	case SIGEV_SIGNAL:
		notified = cmp_ok = 0;
		ev.sigev_signo = SIGUSR1;
		ev.sigev_value.sival_int = USER_DATA;

		memset(&sigact, 0, sizeof(sigact));
		sigact.sa_sigaction = sigfunc;
		sigact.sa_flags = SA_SIGINFO;
		TEST(rc = sigaction(SIGUSR1, &sigact, NULL));
		break;
	case SIGEV_THREAD:
		notified = cmp_ok = 0;
		ev.sigev_notify_function = tfunc;
		ev.sigev_notify_attributes = NULL;
		ev.sigev_value.sival_int = USER_DATA;
		break;
	}

	if (tc->ttype == ALREADY_REGISTERED) {
		TEST(rc = mq_notify(fd, &ev));
		if (TEST_RETURN < 0) {
			tst_resm(TFAIL | TTERRNO, "mq_notify failed");
			result = 1;
			goto EXIT;
		}
	}

	/*
	 * Execute system call
	 */
	errno = 0;
	sys_ret = mq_notify(fd, &ev);
	sys_errno = errno;
	if (sys_ret < 0)
		goto TEST_END;

	/*
	 * Prepare send message
	 */
	for (i = 0; i < MSG_SIZE; i++)
		smsg[i] = i;
	TEST(rc = mq_timedsend(fd, smsg, MSG_SIZE, 0, &abs_timeout));
	if (rc < 0) {
		tst_resm(TFAIL | TTERRNO, "mq_timedsend failed");
		result = 1;
		goto EXIT;
	}

	while (!notified)
		usleep(10000);

TEST_END:
	/*
	 * Check results
	 */
	result |= (sys_ret != 0 && sys_errno != tc->err) || !cmp_ok;
	PRINT_RESULT_CMP(sys_ret >= 0, tc->ret, tc->err, sys_ret, sys_errno,
			 cmp_ok);

EXIT:
	if (fd >= 0) {
		close(fd);
		mq_unlink(QUEUE_NAME);
	}

	return result;
}

static void usage(const char *progname)
{
	tst_resm(TINFO, "usage: %s [options]", progname);
	tst_resm(TINFO, "This is a regression test program of %s system call.",
		 SYSCALL_NAME);
	tst_resm(TINFO, "options:");
	tst_resm(TINFO, "    -d --debug	   Show debug messages");
	tst_resm(TINFO, "    -h --help	    Show this message");
}

int main(int ac, char **av)
{
	int result = RESULT_OK;
	int c;
	int i;
	int lc;

	struct option long_options[] = {
		{"debug", no_argument, 0, 'd'},
		{"help", no_argument, 0, 'h'},
		{NULL, 0, NULL, 0}
	};

	progname = basename(av[0]);

	tst_parse_opts(ac, av, NULL, NULL);

	setup();

	for (lc = 0; TEST_LOOPING(lc); ++lc) {
		tst_count = 0;
		for (testno = 0; testno < TST_TOTAL; ++testno) {
			TEST(c = getopt_long(ac, av, "dh", long_options, NULL));
			while (TEST_RETURN != -1) {
				switch (c) {
				case 'd':
					opt_debug = 1;
					break;
				default:
					usage(progname);
				}
			}

			if (ac != optind) {
				tst_resm(TINFO, "Options are not match.");
				usage(progname);
			}

			for (i = 0; i < (int)(sizeof(tcase) / sizeof(tcase[0]));
			     i++) {
				int ret;
				tst_resm(TINFO, "(case%02d) START", i);
				ret = do_test(&tcase[i]);
				tst_resm(TINFO, "(case%02d) END => %s",
					 i, (ret == 0) ? "OK" : "NG");
				result |= ret;
			}

			switch (result) {
			case RESULT_OK:
				tst_resm(TPASS, "mq_notify call succeeded");
				break;

			default:
				tst_brkm(TFAIL, cleanup, "mq_notify failed");
				break;
			}

		}
	}
	cleanup();
	tst_exit();
}
