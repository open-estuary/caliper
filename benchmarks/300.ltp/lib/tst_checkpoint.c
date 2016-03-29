/*
 * Copyright (C) 2012 Cyril Hrubis chrubis@suse.cz
 * Copyright (C) 2014 Matus Marhefka mmarhefk@redhat.com
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of version 2 of the GNU General Public License as
 * published by the Free Software Foundation.
 *
 * This program is distributed in the hope that it would be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 *
 * Further, this software is distributed without any warranty that it is
 * free of the rightful claim of any third person regarding infringement
 * or the like.  Any license provided herein, whether implied or
 * otherwise, applies only to this software file.  Patent licenses, if
 * any, provided herein do not apply to combinations of this program with
 * other software, or any other product whatsoever.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, write the Free Software Foundation, Inc.,
 * 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <poll.h>

#include "tst_checkpoint.h"

/*
 * Issue open() on 'path' fifo with O_WRONLY flag and wait for
 * a reader up to 'timeout' ms.
 *
 * Returns:
 *   >= 0 - file descriptor
 *   -1  - an error has occurred (errno is set accordingly)
 *
 */
int open_wronly_timed(const char *path, unsigned int timeout)
{
	int fd;
	unsigned int i;
	int interval = 1; /* how often issue open(O_NONBLOCK), in ms */

	for (i = 0; i < timeout; i += interval) {
		fd = open(path, O_WRONLY | O_NONBLOCK);
		if (fd < 0) {
			if ((errno == ENXIO) || (errno == EINTR)) {
				usleep(interval * 1000);

				continue;
			}

			return -1;
		}

		return fd;
	}

	errno = ETIMEDOUT;
	return -1;
}

void tst_checkpoint_init(const char *file, const int lineno,
                         struct tst_checkpoint *self)
{
	static unsigned int fifo_counter = 0;
	int rval;

	/* default values */
	rval = snprintf(self->file, TST_FIFO_LEN, "tst_checkopoint_fifo_%u",
			fifo_counter++);
	if (rval < 0) {
		tst_brkm(TBROK, NULL,
			 "Failed to create a unique temp file name at %s:%d",
			 file, lineno);
	}
	self->retval = 1;
	self->timeout = 5000;
}

void tst_checkpoint_create(const char *file, const int lineno,
			   struct tst_checkpoint *self)

{

	if (!tst_tmpdir_created()) {
		tst_brkm(TBROK, NULL, "Checkpoint could be used only in test "
				      "temporary directory at %s:%d",
				      file, lineno);
	}

	tst_checkpoint_init(file, lineno, self);

	if (mkfifo(self->file, 0666)) {
		tst_brkm(TBROK | TERRNO, NULL,
		         "Failed to create fifo '%s' at %s:%d",
		         self->file, file, lineno);
	}
}

void tst_checkpoint_parent_wait(const char *file, const int lineno,
                                void (*cleanup_fn)(void),
				struct tst_checkpoint *self)
{
	int ret;
	char ch;
	struct pollfd fd;

	fd.fd = open(self->file, O_RDONLY | O_NONBLOCK);

	if (fd.fd < 0) {
		tst_brkm(TBROK | TERRNO, cleanup_fn,
		         "Failed to open fifo '%s' at %s:%d",
		         self->file, file, lineno);
	}

	fd.events = POLLIN;
	fd.revents = 0;

	ret = poll(&fd, 1, self->timeout);

	switch (ret) {
	case 0:
		close(fd.fd);
		tst_brkm(TBROK, cleanup_fn, "Checkpoint timeouted after "
		         "%u msecs at %s:%d", self->timeout, file, lineno);
	break;
	case 1:
	break;
	default:
		tst_brkm(TBROK | TERRNO, cleanup_fn,
		         "Poll failed for fifo '%s' at %s:%d",
			 self->file, file, lineno);
	}

	ret = read(fd.fd, &ch, 1);

	switch (ret) {
	case 0:
		close(fd.fd);
		tst_brkm(TBROK, cleanup_fn,
		         "The other end of the pipe was closed "
		         "unexpectedly at %s:%d", file, lineno);
	break;
	case -1:
		close(fd.fd);
		tst_brkm(TBROK | TERRNO, cleanup_fn,
		         "Failed to read from pipe at %s:%d\n",
		         file, lineno);
	break;
	}

	if (ch != 'c') {
		close(fd.fd);
		tst_brkm(TBROK, cleanup_fn,
		         "Wrong data read from the pipe at %s:%d\n",
		         file, lineno);
	}

	close(fd.fd);
}

void tst_checkpoint_child_wait(const char *file, const int lineno,
                               struct tst_checkpoint *self)
{
	int ret, fd;
	char ch;

	fd = open(self->file, O_RDONLY);

	if (fd < 0) {
		fprintf(stderr, "CHILD: Failed to open fifo '%s': %s at "
		        "%s:%d\n", self->file, strerror(errno),
		        file, lineno);
		exit(self->retval);
	}
	
	ret = read(fd, &ch, 1);

	if (ret == -1) {
		fprintf(stderr, "CHILD: Failed to read from fifo '%s': %s "
		        "at %s:%d\n", self->file, strerror(errno),
		        file, lineno);
		goto err;
	}

	if (ch != 'p') {
		fprintf(stderr, "CHILD: Wrong data read from the pipe "
		        "at %s:%d\n", file, lineno);
		goto err;
	}

	close(fd);
	return;
err:
	close(fd);
	exit(self->retval);
}

void tst_checkpoint_signal_parent(const char *file, const int lineno,
                                  struct tst_checkpoint *self)
{
	int ret, fd;
	
	fd = open(self->file, O_WRONLY);

	if (fd < 0) {
		fprintf(stderr, "CHILD: Failed to open fifo '%s': %s at %s:%d",
		        self->file, strerror(errno), file, lineno);
		exit(self->retval);
	}

	ret = write(fd, "c", 1);

	switch (ret) {
	case 0:
		fprintf(stderr, "No data written, something is really "
		        "screewed; at %s:%d\n", file, lineno);
		goto err;
	break;
	case -1:
		fprintf(stderr, "Failed to write to pipe: %s at %s:%d\n",
		        strerror(errno), file, lineno);
		goto err;
	break;
	}

	close(fd);
	return;
err:
	close(fd);
	exit(self->retval);
}

void tst_checkpoint_signal_child(const char *file, const int lineno,
                                 void (*cleanup_fn)(void),
				 struct tst_checkpoint *self)
{
	int ret, fd;
	
	fd = open_wronly_timed(self->file, self->timeout);

	if (fd < 0) {
		tst_brkm(TBROK | TERRNO, cleanup_fn,
		         "Failed to open fifo '%s' at %s:%d",
		         self->file, file, lineno);
	}

	ret = write(fd, "p", 1);

	switch (ret) {
	case 0:
		close(fd);
		tst_brkm(TBROK, cleanup_fn,
		         "No data written, something is really screewed; "
			 "at %s:%d\n", file, lineno);
	break;
	case -1:
		close(fd);
		tst_brkm(TBROK | TERRNO, cleanup_fn,
		         "Failed to write to pipe at %s:%d\n",
		         file, lineno);
	break;
	}
	
	close(fd);
}
