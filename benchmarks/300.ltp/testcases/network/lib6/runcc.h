/*
 *
 *   Copyright (c) International Business Machines  Corp., 2001
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

int aliascheck(char *tname, char *incl, char *structure, char *field,
	char *dname);
int funccheck(char *tname, char *incl, char *fname);
int structcheck(char *tname, char *incl, char *structure, char *field,
	char *offset, char *size);
int valuecheck(char *tname, char *incl, char *dname, char *dval);

#define IP6_H "#include <netinet/ip6.h>\n"
#define IN_H "#include <netinet/in.h>\n"
#define ICMP6_H "#include <netinet/icmp6.h>\n"
#define SOCKET_H "#include <sys/types.h>\n#include <sys/socket.h>\n"
