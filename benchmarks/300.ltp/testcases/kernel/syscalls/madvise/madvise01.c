/*
 *  Copyright (c) International Business Machines  Corp., 2004
 *  Copyright (c) Linux Test Project, 2013
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU Library General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
 */

/*
 * This is a test case for madvise(2) system call.
 * It tests madvise(2) with combinations of advice values.
 * No error should be returned.
 */

#include <sys/types.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

#include "test.h"

static void setup(void);
static void cleanup(void);
static void check_and_print(char *advice);

char *TCID = "madvise01";
int TST_TOTAL = 5;

int main(int argc, char *argv[])
{
	int lc, fd;
	int i = 0;
	char *file = NULL;
	struct stat stat;
	char filename[64];
	char *progname = NULL;
	char *str_for_file = "abcdefghijklmnopqrstuvwxyz12345\n";

	tst_parse_opts(argc, argv, NULL, NULL);

	setup();

	progname = *argv;
	sprintf(filename, "%s-out.%d", progname, getpid());

	for (lc = 0; TEST_LOOPING(lc); lc++) {
		tst_count = 0;

		fd = open(filename, O_RDWR | O_CREAT, 0664);
		if (fd < 0)
			tst_brkm(TBROK | TERRNO, cleanup, "open failed");
#ifdef DEBUG
		tst_resm(TINFO, "filename = %s opened successfully", filename);
#endif

		/* Writing 40 KB of random data into this file
		   [32 * 1280 = 40960] */
		for (i = 0; i < 1280; i++)
			if (write(fd, str_for_file, strlen(str_for_file)) == -1)
				tst_brkm(TBROK | TERRNO, cleanup,
					 "write failed");

		if (fstat(fd, &stat) == -1)
			tst_brkm(TBROK, cleanup, "fstat failed");

		/* Map the input file into memory */
		file = mmap(NULL, stat.st_size, PROT_READ, MAP_SHARED, fd, 0);
		if (file == MAP_FAILED)
			tst_brkm(TBROK, cleanup, "mmap failed");

		/* (1) Test case for MADV_NORMAL */
		TEST(madvise(file, stat.st_size, MADV_NORMAL));
		check_and_print("MADV_NORMAL");

		/* (2) Test case for MADV_RANDOM */
		TEST(madvise(file, stat.st_size, MADV_RANDOM));
		check_and_print("MADV_RANDOM");

		/* (3) Test case for MADV_SEQUENTIAL */
		TEST(madvise(file, stat.st_size, MADV_SEQUENTIAL));
		check_and_print("MADV_SEQUENTIAL");

		/* (4) Test case for MADV_WILLNEED */
		TEST(madvise(file, stat.st_size, MADV_WILLNEED));
		check_and_print("MADV_WILLNEED");

		/* (5) Test case for MADV_DONTNEED */
		TEST(madvise(file, stat.st_size, MADV_DONTNEED));
		check_and_print("MADV_DONTNEED");

		if (munmap(file, stat.st_size) == -1)
			tst_brkm(TBROK | TERRNO, cleanup, "munmap failed");

		close(fd);
	}

	cleanup();
	tst_exit();
}

static void setup(void)
{

	tst_sig(NOFORK, DEF_HANDLER, cleanup);

	TEST_PAUSE;

	tst_tmpdir();
}

static void cleanup(void)
{
	tst_rmdir();

}

static void check_and_print(char *advice)
{
	if (TEST_RETURN == -1)
		tst_resm(TFAIL | TTERRNO, "madvise test for %s failed", advice);
	else
		tst_resm(TPASS, "madvise test for %s PASSED", advice);
}
