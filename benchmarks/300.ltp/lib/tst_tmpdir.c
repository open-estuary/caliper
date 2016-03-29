/**********************************************************
 * Copyright (c) 2000 Silicon Graphics, Inc.  All Rights Reserved.
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
 *
 * Contact information: Silicon Graphics, Inc., 1600 Amphitheatre Pkwy,
 * Mountain View, CA  94043, or:
 *
 * http://www.sgi.com
 *
 * For further information regarding this notice, see:
 *
 * http://oss.sgi.com/projects/GenInfo/NoticeExplan/
 *********************************************************/

/**********************************************************
 *
 *	 OS Testing - Silicon Graphics, Inc.
 *
 *	 FUNCTION NAME	  : tst_tmpdir, tst_rmdir
 *
 *	 FUNCTION TITLE	 : Create/remove a testing temp dir
 *
 *	 SYNOPSIS:
 *		void tst_tmpdir();
 *		void tst_rmdir();
 *
 *	 AUTHOR		 : Dave Fenner
 *
 *	 INITIAL RELEASE	: UNICOS 8.0
 *
 *	 DESCRIPTION
 *		tst_tmpdir() is used to create a unique, temporary testing
 *		directory, and make it the current working directory.
 *		tst_rmdir() is used to remove the directory created by
 *		tst_tmpdir().
 *
 *	 RETURN VALUE
 *		Neither tst_tmpdir() or tst_rmdir() has a return value.
 *
 *********************************************************/

#include <sys/types.h>
#include <sys/stat.h>
#include <assert.h>
#include <errno.h>
#include <libgen.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "test.h"
#include "rmobj.h"
#include "ltp_priv.h"

/*
 * Define some useful macros.
 */
#define DIR_MODE	(S_IRWXU|S_IRWXG|S_IRWXO)

#ifndef PATH_MAX
#ifdef MAXPATHLEN
#define PATH_MAX	MAXPATHLEN
#else
#define PATH_MAX	1024
#endif
#endif

/*
 * Define function prototypes.
 */
static void tmpdir_cleanup(void);

/*
 * Define global variables.
 */
extern char *TCID;		/* defined/initialized in main() */
static char *TESTDIR = NULL;	/* the directory created */

static char test_start_work_dir[PATH_MAX];


int tst_tmpdir_created(void)
{
	return TESTDIR != NULL;
}

char *tst_get_tmpdir(void)
{
	/* Smack the user for calling things out of order. */
	if (TESTDIR == NULL)
		tst_brkm(TBROK, NULL, "you must call tst_tmpdir() first");
	return strdup(TESTDIR);
}

const char *tst_get_startwd(void)
{
	return test_start_work_dir;
}

void tst_tmpdir(void)
{
	char template[PATH_MAX];
	char *env_tmpdir;
	char *errmsg, *c;

	/*
	 * Create a template for the temporary directory.  Use the
	 * environment variable TMPDIR if it is available, otherwise
	 * use our default TEMPDIR.
	 */
	env_tmpdir = getenv("TMPDIR");
	if (env_tmpdir) {
		c = strchr(env_tmpdir, '/');
		/*
		 * Now we force environment variable TMPDIR to be an absolute
		 * pathname, which dose not make much sense, but it will
		 * greatly simplify code in tst_rmdir().
		 */
		if (c != env_tmpdir) {
			tst_brkm(TBROK, tmpdir_cleanup, "You must specify "
				 "an absolute pathname for environment "
				 "variable TMPDIR");
		}
		snprintf(template, PATH_MAX, "%s/%.3sXXXXXX", env_tmpdir, TCID);
	} else {
		snprintf(template, PATH_MAX, "%s/%.3sXXXXXX", TEMPDIR, TCID);
	}

	/* Make the temporary directory in one shot using mkdtemp. */
	if (mkdtemp(template) == NULL)
		tst_brkm(TBROK | TERRNO, tmpdir_cleanup,
			 "%s: mkdtemp(%s) failed", __func__, template);
	if ((TESTDIR = strdup(template)) == NULL)
		tst_brkm(TBROK | TERRNO, tmpdir_cleanup,
			 "%s: strdup(%s) failed", __func__, template);

	if (chown(TESTDIR, -1, getgid()) == -1)
		tst_brkm(TBROK | TERRNO, tmpdir_cleanup,
			 "chown(%s, -1, %d) failed", TESTDIR, getgid());
	if (chmod(TESTDIR, DIR_MODE) == -1)
		tst_brkm(TBROK | TERRNO, tmpdir_cleanup,
			 "chmod(%s, %#o) failed", TESTDIR, DIR_MODE);

	if (getcwd(test_start_work_dir, sizeof(test_start_work_dir)) == NULL) {
		tst_resm(TINFO, "Failed to record test working dir");
		test_start_work_dir[0] = '\0';
	}

	/*
	 * Change to the temporary directory.  If the chdir() fails, issue
	 * TBROK messages for all test cases, attempt to remove the
	 * directory (if it was created), and exit.  If the removal also
	 * fails, also issue a TWARN message.
	 */
	if (chdir(TESTDIR) == -1) {
		tst_resm(TERRNO, "%s: chdir(%s) failed", __func__, TESTDIR);

		/* Try to remove the directory */
		if (rmobj(TESTDIR, &errmsg) == -1) {
			tst_resm(TWARN, "%s: rmobj(%s) failed: %s",
				 __func__, TESTDIR, errmsg);
		}

		tst_exit();
	}
}

void tst_rmdir(void)
{
	char *errmsg;

	/*
	 * Check that TESTDIR is not NULL.
	 */
	if (TESTDIR == NULL) {
		tst_resm(TWARN,
			 "%s: TESTDIR was NULL; no removal attempted",
			 __func__);
		return;
	}

	/*
	 * Attempt to remove the "TESTDIR" directory, using rmobj().
	 */
	if (rmobj(TESTDIR, &errmsg) == -1) {
		tst_resm(TWARN, "%s: rmobj(%s) failed: %s",
			 __func__, TESTDIR, errmsg);
	}
}

/*
 * tmpdir_cleanup(void) - This function is used when tst_tmpdir()
 *			  encounters an error, and must cleanup and exit.
 *			  It prints a warning message via tst_resm(), and
 *			  then calls tst_exit().
 */
static void tmpdir_cleanup(void)
{
	tst_resm(TWARN,
		 "%s: no user cleanup function called before exiting",
		 __func__);
}
