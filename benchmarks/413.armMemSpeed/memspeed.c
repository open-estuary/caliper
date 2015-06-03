/*
  Copyright (c) 2010 Mans Rullgard

  Permission is hereby granted, free of charge, to any person obtaining
  a copy of this software and associated documentation files (the
  "Software"), to deal in the Software without restriction, including
  without limitation the rights to use, copy, modify, merge, publish,
  distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so, subject to
  the following conditions:

  The above copyright notice and this permission notice shall be
  included in all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
  CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
  TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*/

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <malloc.h>
#include <sys/time.h>
#include <unistd.h>

extern void *memcpy_arm(void *dst, const void *src, size_t size);
extern void *memcpy_vldm_64(void *dst, const void *src, size_t size);
extern void *memcpy_vldm_128(void *dst, const void *src, size_t size);
extern void *memcpy_vld1(void *dst, const void *src, size_t size);
extern void *memcpy_armneon(void *dst, const void *src, size_t size);
extern void *memcpy_androidv5(void *dst, const void *src, size_t size);
extern void *memcpy_androidv7(void *dst, const void *src, size_t size);
extern void *memcpy_ple_neon(void *dst, const void *src, size_t size);
extern void *memcpy_a9(void *dst, const void *src, size_t size);

extern void memread_arm(const void *src, size_t size);
extern void memread_vldm(const void *src, size_t size);
extern void memread_vld1(const void *src, size_t size);
extern void memread_armneon(const void *src, size_t size);
extern void memread_ple_neon(const void *src, size_t size);

extern void *memset_arm(void *dst, int c, size_t size);
extern void *memset_vstm(void *dst, int c, size_t size);
extern void *memset_vst1(void *dst, int c, size_t size);
extern void *memset_armneon(void *dst, int c, size_t size);

#define BUFSIZE (8*1024*1024)
#define __ARM_NEON__

static int iter = 128;

static unsigned
tv_diff(struct timeval *tv1, struct timeval *tv2)
{
    return (tv2->tv_sec - tv1->tv_sec) * 1000000 +
        (tv2->tv_usec - tv1->tv_usec);
}

static void print_stats(const char *tag, const char *name,
                        size_t size, int iter, unsigned time)
{
    uint64_t speed = (uint64_t)size * iter * 1000000 / time;
    printf("%-5s %-12s %4llu MB/s\n", tag, name, speed / 1048576);
}

static void do_copy(const char *name, void *p1, void *p2, size_t size,
                    void *(*cpy)(void *, const void *, size_t))
{
    struct timeval t1, t2;
    int i;

    gettimeofday(&t1, NULL);
    for (i = 0; i < iter; i++)
        cpy(p1, p2, size);
    gettimeofday(&t2, NULL);

    print_stats("copy", name, size, iter, tv_diff(&t1, &t2));
}

static void do_write(const char *name, void *p1, size_t size,
                     void *(*wr)(void *, int, size_t))
{
    struct timeval t1, t2;
    int i;

    gettimeofday(&t1, NULL);
    for (i = 0; i < iter; i++)
        wr(p1, 0, size);
    gettimeofday(&t2, NULL);

    print_stats("write", name, size, iter, tv_diff(&t1, &t2));
}

static void do_read(const char *name, void *p1, size_t size,
                    void (*rd)(const void *, size_t))
{
    struct timeval t1, t2;
    int i;

    gettimeofday(&t1, NULL);
    for (i = 0; i < iter; i++)
        rd(p1, size);
    gettimeofday(&t2, NULL);

    print_stats("read", name, size, iter, tv_diff(&t1, &t2));
}

static void *int32_cpy(void *dst, const void *src, size_t size)
{
    const uint32_t *s = src;
    uint32_t *d = dst;
    int i;

    size /= 4;

    for (i = 0; i < size; i++)
        d[i] = s[i];

    return dst;
}

struct copy_func {
    const char *name;
    int flags;
    void *(*func)(void *, const void *, size_t);
};

struct read_func {
    const char *name;
    int flags;
    void (*func)(const void *, size_t);
};

struct write_func {
    const char *name;
    int flags;
    void *(*func)(void *, int, size_t);
};

struct copy_func copy_tab[] = {
    { "libc",          1, memcpy           },
    { "Android v5",    1, memcpy_androidv5 },
    { "Android NEON",  1, memcpy_androidv7 },
    { "INT32",         2, int32_cpy        },
    { "ASM ARM",       4, memcpy_arm       },
    { "ASM ARM A9",    4, memcpy_a9        },
    { "ASM VLDM 64",   8, memcpy_vldm_64   },
#ifdef __ARM_NEON__
    { "ASM VLDM 128",  8, memcpy_vldm_128  },
    { "ASM VLD1",      8, memcpy_vld1      },
    { "ASM ARM+NEON", 32, memcpy_armneon   },
#ifdef PLE_A8
    { "PLE NEON",     16, memcpy_ple_neon  },
#endif
#endif
};

struct read_func read_tab[] = {
    { "ASM ARM",       4, memread_arm      },
    { "ASM VLDM",      8, memread_vldm     },
#ifdef __ARM_NEON__
    { "ASM VLD1",      8, memread_vld1     },
    { "ASM ARM+NEON", 32, memread_armneon  },
#ifdef PLE_A8
    { "PLE NEON",     16, memread_ple_neon },
#endif
#endif
};

struct write_func write_tab[] = {
    { "libc",           1, memset         },
    { "ASM ARM",        4, memset_arm     },
    { "ASM VSTM",       8, memset_vstm    },
#ifdef __ARM_NEON__
    { "ASM VST1",       8, memset_vst1    },
    { "ASM ARM+NEON",  32, memset_armneon },
#endif
};

#define ARRAY_SIZE(a) (sizeof(a)/sizeof(a[0]))

int main(int argc, char **argv)
{
    size_t bufsize = BUFSIZE;
    size_t offset = 0;
    //int tests = 31;
    int tests = 63;
    int rd = 0, wr = 0, cp = 0;
    void *buf1, *buf2;
    int opt;
    int i;

    while ((opt = getopt(argc, argv, "b:ci:o:rt:w")) != -1) {
        switch (opt) {
        case 'b':
            bufsize = strtol(optarg, NULL, 0) * 1024;
            break;
        case 'c':
            cp = -1;
            break;
        case 'i':
            iter = strtol(optarg, NULL, 0);
            break;
        case 'o':
            offset = strtol(optarg, NULL, 0);
            break;
        case 'r':
            rd = -1;
            break;
        case 't':
            tests = strtol(optarg, NULL, 0);
            break;
        case 'w':
            wr = -1;
            break;
        }
    }

    if (!(rd || wr || cp))
        rd = wr = cp = -1;

    rd &= tests;
    wr &= tests;
    cp &= tests;

    if (offset < bufsize)
        offset += bufsize;

    buf1 = memalign(4096, bufsize + offset);
    buf2 = (char *)buf1 + offset;

    printf("size    %d %dk %dM\n", bufsize, bufsize/1024, bufsize/1048576);
    printf("offset  %d, %d\n", offset, offset - bufsize);
    printf("buffers %p %p\n", buf1, buf2);

    memset(buf1, 0, bufsize + offset);

    for (i = 0; i < ARRAY_SIZE(copy_tab); i++)
        if (cp & copy_tab[i].flags)
            do_copy(copy_tab[i].name, buf1, buf2, bufsize, copy_tab[i].func);

    for (i = 0; i < ARRAY_SIZE(read_tab); i++)
        if (rd & read_tab[i].flags)
            do_read(read_tab[i].name, buf1, bufsize, read_tab[i].func);

    for (i = 0; i < ARRAY_SIZE(write_tab); i++)
        if (wr & write_tab[i].flags)
            do_write(write_tab[i].name, buf1, bufsize, write_tab[i].func);

    free(buf1);

    return 0;
}
