/*
 * Copyright (c) International Business Machines  Corp., 2007
 * Copyright (c) 2014 Fujitsu Ltd.
 *
 * This program is free software;  you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Library General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
 *
 */

#ifndef FALLOCATE_H
#define FALLOCATE_H

#include <sys/types.h>
#include <endian.h>
#include "config.h"
#include "lapi/abisize.h"
#include "linux_syscall_numbers.h"

#if !defined(HAVE_FALLOCATE)
static inline long fallocate(int fd, int mode, loff_t offset, loff_t len)
{
	/* Deal with 32bit ABIs that have 64bit syscalls. */
# if LTP_USE_64_ABI
	return ltp_syscall(__NR_fallocate, fd, mode, offset, len);
# else
	return (long)ltp_syscall(__NR_fallocate, fd, mode,
				 __LONG_LONG_PAIR((off_t) (offset >> 32),
						  (off_t) offset),
				 __LONG_LONG_PAIR((off_t) (len >> 32),
						  (off_t) len));
# endif
}
#endif

#endif /* FALLOCATE_H */
