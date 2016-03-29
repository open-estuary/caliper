/*
 * Copyright (c) Wipro Technologies Ltd, 2002.  All Rights Reserved.
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of version 2 of the GNU General Public License as
 * published by the Free Software Foundation.
 *
 * This program is distributed in the hope that it would be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, write the Free Software Foundation, Inc.,
 * 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 *
 *    AUTHOR		: Nirmala Devi Dhanasekar <nirmala.devi@wipro.com>
 *
 *    DESCRIPTION
 *	Verify that umount(2) returns -1 and sets errno to  EPERM if the user
 *	is not the super-user.
 *
 * RESTRICTIONS
 *	test must be run with the -D option
 *	test doesn't support -c option to run it in parallel, as mount
 *	syscall is not supposed to run in parallel.
 */

#include <errno.h>
#include <sys/mount.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/fcntl.h>
#include <sys/wait.h>
#include <pwd.h>

#include "test.h"
#include "usctest.h"
#include "safe_macros.h"

static void setup(void);
static void cleanup(void);

char *TCID = "umount03";

#define FSTYPE_LEN	20
#define DIR_MODE	S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH
#define MNTPOINT	"mntpoint"

static const char *device;
static int mount_flag;

int TST_TOTAL = 1;

static int exp_enos[] = { EPERM, 0 };

int main(int ac, char **av)
{
	int lc;
	const char *msg;

	if ((msg = parse_opts(ac, av, NULL, NULL)) != NULL)
		tst_brkm(TBROK, NULL, "OPTION PARSING ERROR - %s", msg);

	setup();

	for (lc = 0; TEST_LOOPING(lc); lc++) {
		tst_count = 0;

		TEST(umount(MNTPOINT));

		if (TEST_RETURN != -1) {
			tst_resm(TFAIL, "umout() didn't fail (ret=%ld)",
				 TEST_RETURN);
			continue;
		}

		if (TEST_ERRNO == EPERM) {
			tst_resm(TPASS | TTERRNO, "umount() failed with EPERM");
		} else {
			tst_resm(TFAIL | TTERRNO,
			         "umount() did not fail with EPERM(%d)", EPERM);
		}
	}

	cleanup();
	tst_exit();
}

static void setup(void)
{
	const char *fs_type;
	struct passwd *ltpuser;

	tst_sig(FORK, DEF_HANDLER, cleanup);
	TEST_EXP_ENOS(exp_enos);

	tst_require_root(NULL);

	ltpuser = SAFE_GETPWNAM(NULL, "nobody");

	tst_tmpdir();

	fs_type = tst_dev_fs_type();
	device = tst_acquire_device(cleanup);
	if (!device)
		tst_brkm(TCONF, cleanup, "Failed to obtain block device");

	tst_mkfs(cleanup, device, fs_type, NULL);

	SAFE_MKDIR(cleanup, MNTPOINT, DIR_MODE);

	if (mount(device, MNTPOINT, fs_type, 0, NULL))
		tst_brkm(TBROK | TERRNO, cleanup, "mount() failed");
	mount_flag = 1;

	SAFE_SETEUID(cleanup, ltpuser->pw_uid);
	TEST_PAUSE;
}

static void cleanup(void)
{
	if (seteuid(0))
		tst_resm(TWARN | TERRNO, "seteuid(0) failed");

	if (mount_flag && umount(MNTPOINT))
		tst_resm(TWARN | TERRNO, "umount() failed");

	if (device)
		tst_release_device(NULL, device);

	TEST_CLEANUP;
	tst_rmdir();
}
