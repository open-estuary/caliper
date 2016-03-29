/*
 *
 *   Copyright (c) International Business Machines  Corp., 2004
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
 *	hugeshmget02.c
 *
 * DESCRIPTION
 *	hugeshmget02 - check for ENOENT, EEXIST and EINVAL errors
 *
 * ALGORITHM
 *	create a large shared memory segment with read & write permissions
 *	loop if that option was specified
 *	  call shmget() using five different invalid cases
 *	  check the errno value
 *	    issue a PASS message if we get ENOENT, EEXIST or EINVAL
 *	  otherwise, the tests fails
 *	    issue a FAIL message
 *	call cleanup
 *
 * USAGE:  <for command-line>
 *  hugeshmget02 [-c n] [-e] [-i n] [-I x] [-P x] [-t]
 *     where,  -c n : Run n copies concurrently.
 *             -e   : Turn on errno logging.
 *	       -i n : Execute test n times.
 *	       -I x : Execute test for x seconds.
 *	       -P x : Pause for x seconds between iterations.
 *	       -t   : Turn on syscall timing.
 *
 * HISTORY
 *	03/2001 - Written by Wayne Boyer
 *	04/2004 - Updated by Robbie Williamson
 *
 * RESTRICTIONS
 *	none
 */

#include "hugetlb.h"
#include "safe_macros.h"
#include "mem.h"

char *TCID = "hugeshmget02";
int TST_TOTAL = 4;

static size_t shm_size;
static int shm_id_1 = -1;
static int shm_nonexistent_key = -1;
static key_t shmkey2;

static long hugepages = 128;
static option_t options[] = {
	{"s:", &sflag, &nr_opt},
	{NULL, NULL, NULL}
};

struct test_case_t {
	int *skey;
	int size_coe;
	int flags;
	int error;
} TC[] = {
	/* EINVAL - size is 0 */
	{
	&shmkey2, 0, SHM_HUGETLB | IPC_CREAT | IPC_EXCL | SHM_RW, EINVAL},
	    /* EINVAL - size is larger than created segment */
	{
	&shmkey, 2, SHM_HUGETLB | SHM_RW, EINVAL},
	    /* EEXIST - the segment exists and IPC_CREAT | IPC_EXCL is given */
	{
	&shmkey, 1, SHM_HUGETLB | IPC_CREAT | IPC_EXCL | SHM_RW, EEXIST},
	    /* ENOENT - no segment exists for the key and IPC_CREAT is not given */
	    /* use shm_nonexistend_key (-1) as the key */
	{
	&shm_nonexistent_key, 1, SHM_HUGETLB | SHM_RW, ENOENT}
};

int main(int ac, char **av)
{
	int lc, i;
	int shm_id_2 = -1;

	tst_parse_opts(ac, av, options, NULL);

	if (sflag)
		hugepages = SAFE_STRTOL(NULL, nr_opt, 0, LONG_MAX);

	setup();

	for (lc = 0; TEST_LOOPING(lc); lc++) {
		tst_count = 0;

		for (i = 0; i < TST_TOTAL; i++) {
			/* If this key is existent, just remove it */
			if (*TC[i].skey == -1) {
				shm_id_2 = shmget(*(TC[i].skey), 0, 0);
				if (shm_id_2 != -1)
					shmctl(shm_id_2, IPC_RMID, NULL);
			}

			TEST(shmget(*(TC[i].skey), TC[i].size_coe * shm_size,
				    TC[i].flags));
			if (TEST_RETURN != -1) {
				tst_resm(TFAIL, "shmget succeeded "
					 "unexpectedly");
				continue;
			}
			if (TEST_ERRNO == TC[i].error)
				tst_resm(TPASS | TTERRNO, "shmget failed "
					 "as expected");
			else
				tst_resm(TFAIL | TTERRNO, "shmget failed "
					 "unexpectedly - expect errno=%d, "
					 "got", TC[i].error);
		}
	}
	cleanup();
	tst_exit();
}

void setup(void)
{
	long hpage_size;

	tst_require_root();
	check_hugepage();
	tst_sig(NOFORK, DEF_HANDLER, cleanup);
	tst_tmpdir();

	orig_hugepages = get_sys_tune("nr_hugepages");
	set_sys_tune("nr_hugepages", hugepages, 1);
	hpage_size = read_meminfo("Hugepagesize:") * 1024;

	shm_size = hpage_size * hugepages / 2;
	update_shm_size(&shm_size);

	shmkey = getipckey(cleanup);
	shmkey2 = shmkey + 1;
	shm_id_1 = shmget(shmkey, shm_size, IPC_CREAT | IPC_EXCL | SHM_RW);
	if (shm_id_1 == -1)
		tst_brkm(TBROK | TERRNO, cleanup, "shmget #setup");

	TEST_PAUSE;
}

void cleanup(void)
{
	rm_shm(shm_id_1);

	set_sys_tune("nr_hugepages", orig_hugepages, 0);

	tst_rmdir();
}
