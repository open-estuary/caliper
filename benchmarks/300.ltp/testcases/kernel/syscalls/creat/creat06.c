/*
 *   Copyright (c) International Business Machines  Corp., 2001
 *    Ported by Wayne Boyer
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
 *   along with this program;  if not, write to the Free Software Foundation,
 *   Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
 */

/*
 * DESCRIPTION
 *	Testcase to check creat(2) sets the following errnos correctly:
 *	1.	EISDIR
 *	2.	ENAMETOOLONG
 *	3.	ENOENT
 *	4.	ENOTDIR
 *	5.	EFAULT
 *	6.	EACCES
 *	7.	ELOOP
 *	8.	EROFS
 *
 *
 * ALGORITHM
 *	1.	Attempt to creat(2) an existing directory, and test for
 *		EISDIR
 *	2.	Attempt to creat(2) a file whose name is more than
 *		VFS_MAXNAMLEN and test for ENAMETOOLONG.
 *	3.	Attempt to creat(2) a file inside a directory which doesn't
 *		exist, and test for ENOENT
 *	4.	Attempt to creat(2) a file, the pathname of which comprises
 *		a component which is a file, test for ENOTDIR.
 *	5.	Attempt to creat(2) a file with a bad address
 *		and test for EFAULT
 *	6.	Attempt to creat(2) a file in a directory with no
 *		execute permission and test for EACCES
 *	7.	Attempt to creat(2) a file which links the other file that
 *		links the former and test for ELOOP
 *	8.	Attempt to creat(2) a file in a Read-only file system
 *		and test for EROFS
 */

#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <pwd.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/mount.h>
#include "test.h"
#include "safe_macros.h"

#define	TEST_FILE	"test_dir"
#define	NO_DIR		"testfile/testdir"
#define	NOT_DIR		"file1/testdir"
#define	TEST6_FILE	"dir6/file6"
#define	TEST7_FILE	"file7"
#define	TEST8_FILE	"mntpoint/tmp"

#define	MODE1		0444
#define	MODE2		0666

static void setup(void);
static void cleanup(void);
static void test6_setup(void);
static void test6_cleanup(void);
#if !defined(UCLINUX)
static void bad_addr_setup(int);
#endif

static char long_name[PATH_MAX+2];
static const char *device;
static int mount_flag;

static struct test_case_t {
	char *fname;
	int mode;
	int error;
	void (*setup)();
	void (*cleanup)(void);
} TC[] = {
	{TEST_FILE, MODE1, EISDIR, NULL, NULL},
	{long_name, MODE1, ENAMETOOLONG, NULL, NULL},
	{NO_DIR, MODE1, ENOENT, NULL, NULL},
	{NOT_DIR, MODE1, ENOTDIR, NULL, NULL},
#if !defined(UCLINUX)
	{NULL, MODE1, EFAULT, bad_addr_setup, NULL},
#endif
	{TEST6_FILE, MODE1, EACCES, test6_setup, test6_cleanup},
	{TEST7_FILE, MODE1, ELOOP, NULL, NULL},
	{TEST8_FILE, MODE1, EROFS, NULL, NULL},
};

char *TCID = "creat06";
int TST_TOTAL = ARRAY_SIZE(TC);
static struct passwd *ltpuser;

int main(int ac, char **av)
{
	int lc;
	int i;

	tst_parse_opts(ac, av, NULL, NULL);

	setup();

	for (lc = 0; TEST_LOOPING(lc); lc++) {

		tst_count = 0;

		for (i = 0; i < TST_TOTAL; i++) {

			if (TC[i].setup != NULL)
				TC[i].setup(i);

			TEST(creat(TC[i].fname, TC[i].mode));

			if (TC[i].cleanup != NULL)
				TC[i].cleanup();

			if (TEST_RETURN != -1) {
				tst_resm(TFAIL, "call succeeded unexpectedly");
				continue;
			}

			if (TEST_ERRNO == TC[i].error) {
				tst_resm(TPASS | TTERRNO,
					 "got expected failure");
			} else {
				tst_resm(TFAIL | TTERRNO, "wanted errno %d",
					 TC[i].error);
			}
		}
	}

	cleanup();
	tst_exit();
}

static void setup(void)
{
	const char *fs_type;

	tst_require_root();

	ltpuser = SAFE_GETPWNAM(cleanup, "nobody");

	tst_sig(NOFORK, DEF_HANDLER, cleanup);

	TEST_PAUSE;

	tst_tmpdir();

	fs_type = tst_dev_fs_type();
	device = tst_acquire_device(cleanup);

	if (!device)
		tst_brkm(TCONF, cleanup, "Failed to acquire device");

	SAFE_MKDIR(cleanup, TEST_FILE, MODE2);

	memset(long_name, 'a', PATH_MAX+1);

	SAFE_TOUCH(cleanup, "file1", MODE1, NULL);

	SAFE_MKDIR(cleanup, "dir6", MODE2);

	SAFE_SYMLINK(cleanup, TEST7_FILE, "test_file_eloop2");
	SAFE_SYMLINK(cleanup, "test_file_eloop2", TEST7_FILE);

	tst_mkfs(cleanup, device, fs_type, NULL);
	SAFE_MKDIR(cleanup, "mntpoint", 0777);
	if (mount(device, "mntpoint", fs_type, MS_RDONLY, NULL) < 0) {
		tst_brkm(TBROK | TERRNO, cleanup,
			 "mount device:%s failed", device);
	}
	mount_flag = 1;
}

#if !defined(UCLINUX)
static void bad_addr_setup(int i)
{
	TC[i].fname = SAFE_MMAP(cleanup, 0, 1, PROT_NONE,
			     MAP_PRIVATE | MAP_ANONYMOUS, 0, 0);
}
#endif

static void test6_setup(void)
{
	SAFE_SETEUID(cleanup, ltpuser->pw_uid);
}

static void test6_cleanup(void)
{
	SAFE_SETEUID(cleanup, 0);
}

static void cleanup(void)
{
	if (mount_flag && tst_umount("mntpoint") < 0) {
		tst_brkm(TBROK | TERRNO, NULL,
			 "umount device:%s failed", device);
	}

	if (device)
		tst_release_device(NULL, device);

	tst_rmdir();
}
