/*
 * Copyright (c) 2004, Bull SA. All rights reserved.
 * Created by:  Laurent.Vivier@bull.net
 * This file is licensed under the GPL license.  For the full content
 * of this license, see the COPYING file at the top level of this 
 * source tree.
 */

/*
 * assertion:
 *
 * aio_read() shall fail with [EBADF] or the error status of the operation
 * shall be [EBADF] if aio_fildes argument is not a valid file descriptor open for
 * reading.
 *
 * method:
 *
 *	- Create an aiocb with an invalid aio_filedes
 *	- call aio_read with this aiocb
 *	- check return code and errno
 */

#define _XOPEN_SOURCE 600
#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <string.h>
#include <errno.h>
#include <stdlib.h>
#include <aio.h>

#include "posixtest.h"

#define TNAME "aio_read/10-1.c"

int main()
{
#define BUF_SIZE 111
	char buf[BUF_SIZE];
	struct aiocb aiocb;

#if _POSIX_ASYNCHRONOUS_IO != 200112L
	exit(PTS_UNSUPPORTED);
#endif

	memset(buf, 0xaa, BUF_SIZE);
	memset(&aiocb, 0, sizeof(struct aiocb));
	aiocb.aio_fildes = -1;
	aiocb.aio_buf = buf;
	aiocb.aio_nbytes = BUF_SIZE;

	if (aio_read(&aiocb) != -1)
	{
		printf(TNAME " bad aio_read return value()\n");
		exit(PTS_FAIL);
	}

	if (errno != EBADF)
	{
		printf(TNAME " errno is not EBADF %s\n", strerror(errno));
		exit(PTS_FAIL);
	}


	printf ("Test PASSED\n");
	return PTS_PASS;
}
