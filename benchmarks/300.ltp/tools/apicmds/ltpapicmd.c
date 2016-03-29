/*
 * Copyright (c) International Business Machines  Corp., 2001
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
 */

/*
 * File:        ltpapicmd.c
 *
 * Description: This program impliments a command line version of some of the
 *              LTP harness API's. This will enable tests written in shell and
 *              other scripts to report problems and log results in the LTP
 *              harness format. The intent is to have a common format in which
 *              the C tests and tests written in scripts report results in
 *              a common format.
 *
 *              The following LTP API's are available currently in command line
 *              form:
 *              tst_brk   - Print result message and break remaining test cases
 *              tst_brkm  - Print result message, including file contents, and
 *                          break remaining test cases
 *              tst_res   - Print result message, including file contents
 *              tst_resm  - Print result message
 *              tst_flush - Print any messages pending because of CONDENSE mode,
 *                          and flush output stream
 *              tst_exit  - Exit test with a meaningful exit value
 *
 *              These are the minimum set of functions or commands required to
 *              report results.
 *
 * Exit:        All commands exit with
 *               0   - on success
 *              -1  - on failure
 *
 * Description: Unlike the above commands tst_kvercmp, tst_kvercmp2 have an unusual
 *              exit status
 *              tst_kvercmp  - Compare running kernel to specified version
 *              tst_kvercmp2 - Compare running kernel to specified vanilla version
 *                             or distribution specific version
 * Exit:
 *               2 - running newer kernel
 *               1 - running same age kernel
 *               0 - running older kernel
 *              -1 - on failure
 * History
 * Dec 10 2002 - Created - Manoj Iyer manjo@mail.utexas.edu
 * Dec 12 2002 - Modified - Code that checked if the environment variables
 *               TCID and TST_TOTAL were set did not print usage message.
 *               Modified code to print usage message in each case.
 * Dec 16 2002 - Modified - Code to get the test number, gets environment
 *               variable TST_COUNT and initializes tst_count.
 * Dec 16 2002 - Documentation and comment changes.
 * Feb 11 2003 - tst_count was set to -1 during init or setup in the script.
 *               this was causing tst_resm to issue a warning message.
 *               This bug is now fixed.
 *
 */

#include <sys/socket.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>
#include "test.h"
#include "usctest.h"
#include "safe_macros.h"

char *TCID;			/* Name of the testcase */
int TST_TOTAL;			/* Total number of testcases */

static char cmd_name[1024];	/* name by which this program is invoked tst_brk etc */
static char *tst_total;		/* total number of tests in the file. */
static char *tst_cntstr;	/* sets the value of tst_count with this value */


/*
 * Function:    ident_ttype - Return test result type.
 *
 * Description: This function will return the test result type, it actually
 *              the string that is entered by the user to an integer value that
 *              is understood by the API's.
 *
 * Return:      test type TPASS, TFAIL, TBROK, TCONF, TWARN, or TINFO
 *              on success
 *              -1 on failure
 */
int ident_ttype(char *tstype)
{
	/* test result type one of TPASS, TFAIL, etc */
	if (strcmp(tstype, "TBROK") == 0)
		return TBROK;
	else if (strcmp(tstype, "TFAIL") == 0)
		return TFAIL;
	else if (strcmp(tstype, "TPASS") == 0)
		return TPASS;
	else if (strcmp(tstype, "TCONF") == 0)
		return TCONF;
	else if (strcmp(tstype, "TWARN") == 0)
		return TWARN;
	else if (strcmp(tstype, "TINFO") == 0)
		return TINFO;
	else
		return -1;
}

void apicmd_brk(int argc, char *argv[])
{
	int trestype;
	char *file_name;

	if (argc < 5) {
		fprintf(stderr, "Usage: %s TTYPE FNAME FUNC STRING\n"
			"\tTTYPE  - Test Result Type; one of TFAIL, TBROK "
			"and TCONF.\n"
			"\tFNAME  - Print contents of this file after the message\n"
			"\tFUNC   - Cleanup function (ignored), but MUST be provided\n"
			"\tSTRING - Message explaining the test result\n",
			cmd_name);
		exit(1);
	}
	trestype = ident_ttype((argv++)[0]);
	file_name = (argv++)[0];
	tst_cat_file(file_name);
	argv++;
	tst_brkm(trestype, NULL, "%s", *argv);

}

void apicmd_res(int argc, char *argv[])
{
	int trestype;
	char *file_name;

	if (argc < 4) {
		fprintf(stderr, "Usage: %s TTYPE FNAME STRING\n"
			"\tTTYPE  - Test Result Type; one of TFAIL, TBROK "
			"and  TCONF.\n"
			"\tFNAME  - Print contents of this file after the message\n"
			"\tSTRING - Message explaining the test result\n",
			cmd_name);
		exit(1);
	}
	trestype = ident_ttype((argv++)[0]);
	file_name = (argv++)[0];
	tst_cat_file(file_name);
	tst_resm(trestype, "%s", *argv);
}

void apicmd_brkm(int argc, char *argv[])
{
	int trestype;

	if (argc < 4) {
		fprintf(stderr, "Usage: %s TTYPE FUNC STRING\n"
			"\tTTYPE  - Test Result Type; one of TFAIL, TBROK "
			"and TCONF.\n"
			"\tFUNC   - Cleanup function (ignored), but MUST be provided\n"
			"\tSTRING - Message explaining the test result\n",
			cmd_name);
		exit(1);
	}
	trestype = ident_ttype((argv++)[0]);
	argv++;
	tst_brkm(trestype, NULL, "%s", *argv);
}

void apicmd_resm(int argc, char *argv[])
{
	int trestype;

	if (argc < 3) {
		fprintf(stderr, "Usage: %s TTYPE STRING\n"
			"\tTTYPE  - Test Result Type; one of TFAIL, TBROK"
			"and TCONF.\n"
			"\tSTRING - Message explaining the test result\n",
			cmd_name);
		exit(1);
	}
	trestype = ident_ttype((argv++)[0]);
	tst_resm(trestype, "%s", *argv);
}

void apicmd_kvercmp(int argc, char *argv[])
{
	int exit_value;

	if (argc < 4) {
		fprintf(stderr, "Usage: %s NUM NUM NUM\n"
			"Compares to the running kernel version.\n\n"
			"\tNUM - A positive integer.\n"
			"\tThe first NUM is the kernel VERSION\n"
			"\tThe second NUM is the kernel PATCHLEVEL\n"
			"\tThe third NUM is the kernel SUBLEVEL\n\n"
			"\tExit status is 0 if the running kernel is older than the\n"
			"\t\tkernel specified by NUM NUM NUM.\n"
			"\tExit status is 1 for kernels of the same age.\n"
			"\tExit status is 2 if the running kernel is newer.\n",
			cmd_name);
		exit(1);
	}
	exit_value = tst_kvercmp(atoi(argv[0]), atoi(argv[1]),
				atoi(argv[2]));
	if (exit_value < 0)
		exit_value = 0;
	else if (exit_value == 0)
		exit_value = 1;
	else if (exit_value > 0)
		exit_value = 2;
	exit(exit_value);
}

void apicmd_kvercmp2(int argc, char *argv[])
{
	int exit_value;

	struct tst_kern_exv vers[100];
	unsigned int count;

	char *saveptr1 = NULL;
	char *saveptr2 = NULL;
	char *token1;

	if (TCID == NULL)
		TCID = "outoftest";
	if (tst_cntstr == NULL)
		tst_count = 0;

	if (argc < 5) {
		fprintf(stderr, "Usage: %s NUM NUM NUM KVERS\n"
			"Compares to the running kernel version\n"
			"based on vanilla kernel version NUM NUM NUM\n"
			"or distribution specific kernel version KVERS\n\n"
			"\tNUM - A positive integer.\n"
			"\tThe first NUM is the kernel VERSION\n"
			"\tThe second NUM is the kernel PATCHLEVEL\n"
			"\tThe third NUM is the kernel SUBLEVEL\n\n"
			"\tKVERS is a string of the form "
			"\"DISTR1:VERS1 DISTR2:VERS2\",\n"
			"\twhere DISTR1 is a distribution name\n"
			"\tand VERS1 is the corresponding kernel version.\n"
			"\tExample: \"RHEL6:2.6.39-400.208\"\n\n"
			"\tIf running kernel matches a distribution in KVERS then\n"
			"\tcomparison is performed based on version in KVERS,\n"
			"\totherwise - based on NUM NUM NUM.\n\n"
			"\tExit status is 0 if the running kernel is older.\n"
			"\tExit status is 1 for kernels of the same age.\n"
			"\tExit status is 2 if the running kernel is newer.\n",
			cmd_name);
		exit(3);
	}

	count = 0;
	token1 = strtok_r(argv[3], " ", &saveptr1);
	while ((token1 != NULL) && (count < 99)) {
		vers[count].dist_name = strtok_r(token1, ":", &saveptr2);
		vers[count].extra_ver = strtok_r(NULL, ":", &saveptr2);

		if (vers[count].extra_ver == NULL) {
			fprintf(stderr, "Incorrect KVERS format\n");
			exit(3);
		}

		count++;

		token1 = strtok_r(NULL, " ", &saveptr1);
	}
	vers[count].dist_name = NULL;
	vers[count].extra_ver = NULL;

	exit_value = tst_kvercmp2(atoi(argv[0]), atoi(argv[1]),
				atoi(argv[2]), vers);

	if (exit_value < 0)
		exit_value = 0;
	else if (exit_value == 0)
		exit_value = 1;
	else if (exit_value > 0)
		exit_value = 2;
	exit(exit_value);
}

struct param_pair {
	char *cmd;
	int value;
};

unsigned short apicmd_get_unused_port(int argc, char *argv[])
{
	if (argc != 3)
		goto err;

	const struct param_pair params[][3] = {
		{{"ipv4", AF_INET}, {"ipv6", AF_INET6}, {NULL, 0}},
		{{"stream", SOCK_STREAM}, {"dgram", SOCK_DGRAM}, {NULL, 0}}
	};

	int i;
	const struct param_pair *p[2];
	for (i = 0; i < 2; ++i) {
		for (p[i] = params[i]; p[i]->cmd; ++p[i]) {
			if (!strcmp(p[i]->cmd, argv[i]))
				break;
		}
		if (!p[i]->cmd)
			goto err;
	}
	return  tst_get_unused_port(NULL, p[0]->value, p[1]->value);

err:
	fprintf(stderr, "Usage: tst_get_unused_port FAMILY TYPE\n"
		"where FAMILY := { ipv4 | ipv6 }\n"
		"      TYPE := { stream | dgram }\n");
	exit(1);
}

int apicmd_fs_has_free(int argc, char *argv[])
{
	if (argc != 3) {
		fprintf(stderr, "Usage: tst_fs_has_free path required_bytes\n"
			"path: the pathname of the mounted filesystem\n"
			"required_bytes: the required free space"
			" (supports kB, MB and GB suffixes)\n");
		exit(2);
	}

	char *endptr;
	unsigned int required_kib = strtoull(argv[1], &endptr, 0);
	unsigned int mul = TST_BYTES;

	if (*argv[1] == '\0')
		goto fs_has_free_err;

	if (*endptr != '\0') {
		if (!strcasecmp(endptr, "kB")) {
			mul = TST_KB;
		} else if (!strcasecmp(endptr, "MB")) {
			mul = TST_MB;
		} else if (!strcasecmp(endptr, "GB")) {
			mul = TST_GB;
		} else {
			goto fs_has_free_err;
		}
	}

	exit(!tst_fs_has_free(NULL, argv[0], required_kib, mul));

fs_has_free_err:
	fprintf(stderr, "%s is not a valid size\n", argv[1]);
	exit(2);
}

/*
 * Function:    main - entry point of this program
 *
 * Description: Parses the arguments to each command. Most commands have in
 *              common atlest 2 arguments, type of test result, which is one of
 *              TPASS, TFAIL, TBROK, TCONF, etc, and a message that describes
 *              the result. Other arguments are a file, the contents of which
 *              are printed after the type of test result and associated message
 *              is printed, also a cleanup function that will be executed.
 *              Currently this function name is ignored but MUST be provided
 *              for compatability reasons.
 *
 *              The different commands are actually a hard link to this program
 *              the program invokes the appropriate function based on the
 *              command name with which it was invoked.
 *
 *              Set the values for TCID to the name of the test case.
 *              set the value for TST_TOTAL for total number of tests this is
 *              required in case one test breaks and all following tests also
 *              should be reported as broken.
 *              Set tst_count before every individual test.
 *
 * Exit:        0 on success
 *              -1 on failure
 */
int main(int argc, char *argv[])
{
	strcpy(cmd_name, SAFE_BASENAME(NULL, (argv++)[0]));

	TCID = getenv("TCID");
	tst_total = getenv("TST_TOTAL");
	tst_cntstr = getenv("TST_COUNT");
	if (TCID == NULL || tst_total == NULL || tst_cntstr == NULL) {
		if (!strcmp(cmd_name, "tst_kvercmp") &&
		    !strcmp(cmd_name, "tst_kvercmp2") &&
		    !strcmp(cmd_name, "tst_fs_has_free") &&
		    !strcmp(cmd_name, "tst_get_unused_port")) {
			fprintf(stderr,
				"\nSet variables TCID, TST_TOTAL, and TST_COUNT before each test:\n"
				"export TCID=<test name>\n"
				"export TST_TOTAL=<Total Number of Tests >\n"
				"export TST_COUNT=<Test case number>\n\n");
			/* Make sure the user knows there's an error. */
			abort();
		}
	} else {
		TST_TOTAL = atoi(tst_total);
		tst_count = atoi(tst_cntstr);
		if (tst_count > 0)
			tst_count--;

		if (strcmp(TCID, " ") == 0) {
			fprintf(stderr,
				"Variable TCID not set, use: TCID=<test name>\n");
			exit(1);
		}
		if (TST_TOTAL <= 0) {
			fprintf(stderr,
				"Variable TST_TOTAL is set to 0, must be "
				"greater than zero\n");
			exit(1);
		}
	}

	if (strcmp(cmd_name, "tst_brk") == 0) {
		apicmd_brk(argc, argv);
	} else if (strcmp(cmd_name, "tst_res") == 0) {
		apicmd_res(argc, argv);
	} else if (strcmp(cmd_name, "tst_brkm") == 0) {
		apicmd_brkm(argc, argv);
	} else if (strcmp(cmd_name, "tst_resm") == 0) {
		apicmd_resm(argc, argv);
	} else if (strcmp(cmd_name, "tst_exit") == 0) {
		tst_exit();
	} else if (strcmp(cmd_name, "tst_flush") == 0) {
		tst_flush();
	} else if (strcmp(cmd_name, "tst_kvercmp") == 0) {
		apicmd_kvercmp(argc, argv);
	} else if (strcmp(cmd_name, "tst_kvercmp2") == 0) {
		apicmd_kvercmp2(argc, argv);
	} else if (strcmp(cmd_name, "tst_ncpus") == 0) {
		printf("%li\n", tst_ncpus());
	} else if (strcmp(cmd_name, "tst_ncpus_conf") == 0) {
		printf("%li\n", tst_ncpus_conf());
	} else if (strcmp(cmd_name, "tst_ncpus_max") == 0) {
		printf("%li\n", tst_ncpus_max());
	} else if (strcmp(cmd_name, "tst_get_unused_port") == 0) {
		printf("%u\n", apicmd_get_unused_port(argc, argv));
	} else if (strcmp(cmd_name, "tst_fs_has_free") == 0) {
		apicmd_fs_has_free(argc, argv);
	}

	exit(0);
}
