#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>
#include <sys/time.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

/* to verify memory mmap option
 *  armeb-linux-gnueabi-gcc -O2 -mfpu=vfp -mfloat-abi=softfp -march=armv7-a -o memcpy memcpy.c -lrt
 */

#define MAPSIZE         0x10000
#define REPEATS         10000
#define MEMMB           ((MAPSIZE * REPEATS)/ 0x100000)

int mode = 0;

extern void *bsp_memcpy(void *dest, const void *src, size_t n);
void SRIO_memcpy32(unsigned int  ulDstAddr, unsigned int ulSrcAddr, unsigned int ulLen)
{
        if ((ulLen & 0x1f) || (ulDstAddr & 0x3) || (ulSrcAddr & 0x3)) {
                return;
        }

        __asm volatile(
        "1:"
        "LDMIA %1!, {r3-r10};"
        "STMIA %0!, {r3-r10};"
        "SUB   %2, %2, #0x20;"
        "CMP   %2, #0x0;"
        "BNE   1b;"
        :
        :"r"(ulDstAddr),"r"(ulSrcAddr),"r"(ulLen)
        :"r10","r3","r4","r5","r6","r7","r8","r9","memory");
        return;
}

static inline void __memcpy(void *dest, void *src, unsigned int len)
{
   if (mode == 0) {
      memcpy(dest, src, len);
   } else if (mode == 1) {
      bsp_memcpy(dest, src, len);
   } else {
      if ((len & 0x1f) || (((unsigned int)dest) & 0x3) || (((unsigned int)src) & 0x3)) {
          memcpy(dest, src, len);
      } else {
          SRIO_memcpy32((unsigned int)dest, (unsigned int)src, len);
      }
   }
}


static void ReadMem(void *dest, void *map_base, unsigned int mapped_size, unsigned int stride) {
   unsigned int offset;

   offset = 0;
   while (offset < mapped_size) {
      __memcpy(dest, map_base, stride);
      dest     += stride;
      map_base += stride;
      offset   += stride;
   }
}

static void WriteMem(void *dest, void *map_base, unsigned int mapped_size, unsigned int stride) {
        unsigned int offset;

        offset = 0;
        while (offset < mapped_size) {
      __memcpy(map_base, dest, stride);
                dest     += stride;
                map_base += stride;
                offset   += stride;
        }
}

static int ReadPerf(void *dest, void *map_base, unsigned int mapped_size, unsigned int stride) {
   unsigned int i, repeats;
   struct timeval before, after;
   unsigned int interval, remainder;

   repeats = REPEATS;

   gettimeofday(&before, NULL);
   for (i=0; i<repeats; i++) {
      ReadMem(dest, map_base, mapped_size, stride);
   }
   gettimeofday(&after, NULL);

        interval = (after.tv_sec - before.tv_sec) * 1000000;
        interval += (after.tv_usec - before.tv_usec);
   remainder = interval % 100000;
   interval  = interval / 100000;
   if (remainder > 50000)
      interval++;
   return (MEMMB * 10)/interval;
}

static int WritePerf(void *dest, void *map_base, unsigned int mapped_size, unsigned int stride) {
        unsigned int i, repeats;
        struct timeval before, after;
        int interval, remainder;

        repeats = REPEATS;

        gettimeofday(&before, NULL);
        for (i=0; i<repeats; i++) {
                WriteMem(dest, map_base, mapped_size, stride);
        }
        gettimeofday(&after, NULL);

        interval = (after.tv_sec - before.tv_sec) * 1000000;
        interval += (after.tv_usec - before.tv_usec);
        remainder = interval % 1000000;
        interval  = interval / 1000000;
        if (remainder > 500000)
                interval++;
        return MEMMB/interval;
}


void verifyMem(void *dest, unsigned int mapped_phy, int op) {
   int fd, flags;
   unsigned int mapped_size;
   void *map_base;
   unsigned int stride;
   int speed;

   mapped_size = MAPSIZE;
   flags = O_RDWR;
   if (op & 0xFFFF0000) {
      flags |= O_SYNC;
      op = op & 0xFFFF;
   }

   fd = open("/dev/mem", flags);
        map_base = mmap(NULL,
                        mapped_size,
                        PROT_READ | PROT_WRITE,
                        MAP_SHARED,
                        fd,
                        mapped_phy);

   if (map_base == NULL) {
      close(fd);
      printf("Fail to mmap memory \n");
   }


   if (op == 0) {
      mode = 0;
      stride = 32;
      speed = ReadPerf(dest, map_base, mapped_size, stride);
      printf("speed %d MByte/s for stride %d at phyaddr %lx with memcpy mode %d \n", speed, stride, mapped_phy, mode);
      stride = mapped_size;
      speed = ReadPerf(dest, map_base, mapped_size, stride);
      printf("speed %d MByte/s for stride %d at phyaddr %lx with memcpy mode %d \n", speed, stride, mapped_phy, mode);

      mode = 1;
                stride = 32;
                speed = ReadPerf(dest, map_base, mapped_size, stride);
                printf("speed %d MByte/s for stride %d at phyaddr %lx with memcpy mode %d \n", speed, stride, mapped_phy, mode);
      stride = mapped_size;
                speed = ReadPerf(dest, map_base, mapped_size, stride);
                printf("speed %d MByte/s for stride %d at phyaddr %lx with memcpy mode %d \n", speed, stride, mapped_phy, mode);

                mode = 2;
                stride = 32;
                speed = ReadPerf(dest, map_base, mapped_size, stride);
                printf("speed %d MByte/s for stride %d at phyaddr %lx with memcpy mode %d \n", speed, stride, mapped_phy, mode);
      stride = mapped_size;
                speed = ReadPerf(dest, map_base, mapped_size, stride);
                printf("speed %d MByte/s for stride %d at phyaddr %lx with memcpy mode %d \n", speed, stride, mapped_phy, mode);

   } else {
      mode = 0;
      stride = 32;
      speed = WritePerf(dest, map_base, mapped_size, stride);
      printf("speed %d MByte/s for stride %d at phyaddr %lx with memcpy mode %d \n", speed, stride, mapped_phy, mode);
      stride = 64;
      speed = WritePerf(dest, map_base, mapped_size, stride);
      printf("speed %d MByte/s for stride %d at phyaddr %lx with memcpy mode %d \n", speed, stride, mapped_phy, mode);

                mode = 1;
                stride = 32;
                speed = WritePerf(dest, map_base, mapped_size, stride);
                printf("speed %d MByte/s for stride %d at phyaddr %lx with memcpy mode %d \n", speed, stride, mapped_phy, mode);
                stride = 64;
                speed = WritePerf(dest, map_base, mapped_size, stride);
                printf("speed %d MByte/s for stride %d at phyaddr %lx with memcpy mode %d \n", speed, stride, mapped_phy, mode);
   }


        munmap(map_base, mapped_size);
        close(fd);
   printf("\n");
}

int main() {
   unsigned int mapped_phy;
   void *dest;

   dest = malloc(MAPSIZE * 2);
   if (dest == NULL) {
      printf("Fail to allocate memory \n");
      return -1;
   }


   mapped_phy  =  2044 * 1024 * 1024;
   verifyMem(dest, mapped_phy, 0);
   verifyMem(dest, mapped_phy, 0x10000);
   free(dest);
   return 0;
}
