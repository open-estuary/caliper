#include<linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/slab.h>
#include <linux/io.h>
#include <asm/io.h>

#define MAPSIZE         0x10000
#define REPEATS         10000
#define MEMMB           ((MAPSIZE * REPEATS)/ 0x100000)

static void ReadMem(void *dest, void *map_base, unsigned int mapped_size, unsigned int stride) {
        unsigned int offset;

        offset = 0;
        while (offset < mapped_size) {
                memcpy(dest, map_base, stride);
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

   do_gettimeofday(&before);
   for (i=0; i<repeats; i++) {
      ReadMem(dest, map_base, mapped_size, stride);
   }
   do_gettimeofday(&after);

   interval = (after.tv_sec - before.tv_sec) * 1000000;
   interval += (after.tv_usec - before.tv_usec);
   remainder = interval % 100000;
   interval  = interval / 100000;
   if (remainder > 50000)
      interval++;
   return (MEMMB * 10)/interval;
}

void verifyMem(void *dest, unsigned int mapped_phy, int op) {
        unsigned int mapped_size;
        void *map_base;
        unsigned int stride;
        int speed;

        mapped_size = MAPSIZE;
   if ((op & 0xFFFF0000) == 0) {
      map_base = ioremap(mapped_phy, mapped_size);
   } else if ((op & 0xFFFF0000) == 0x10000) {
      map_base = ioremap_wc(mapped_phy, mapped_size);
        } else if ((op & 0xFFFF0000) == 0x20000) {
//    map_base = ioremap_cache(mapped_phy, mapped_size);
      map_base = __arm_ioremap(mapped_phy, mapped_size, MT_DEVICE_CACHED);
   } else {
      map_base = kmalloc(mapped_size, GFP_KERNEL);
   }

        if (map_base == NULL) {
                printk("Fail to ioremap memory at %x \n", mapped_phy);
      return;
        }

   stride = 1024;
   speed = ReadPerf(dest, map_base, mapped_size, stride);
   printk("speed %d MByte/s for stride %d at phyaddr %x with memcpy op %d \n", speed, stride, mapped_phy, op);

   stride = mapped_size;
   speed = ReadPerf(dest, map_base, mapped_size, stride);
   printk("speed %d MByte/s for stride %d at phyaddr %x with memcpy op %d \n", speed, stride, mapped_phy, op);

   speed = ReadPerf(map_base, dest, mapped_size, stride);
        printk("speed %d MByte/s for stride %d at phyaddr %x with memcpy op %d \n", speed, stride, mapped_phy, op);

   if ((op & 0xFFFF0000) == 0x30000) {
      kfree(map_base);
   } else {
           iounmap(map_base);
   }
        printk("\n");
}

static int __init kernmem_init(void)
{
   printk(KERN_ALERT "Hello World\n");

        unsigned int mapped_phy;
        void *dest;

        dest = kmalloc(MAPSIZE * 2, GFP_KERNEL);
        if (dest == NULL) {
                printk("Fail to allocate memory \n");
                return -1;
        }


        //mapped_phy  =  0;
   mapped_phy = 2046 * 1024 * 1024;
        verifyMem(dest, mapped_phy, 0);
        verifyMem(dest, mapped_phy, 0x10000);
        verifyMem(dest, mapped_phy, 0x20000);
        verifyMem(dest, mapped_phy, 0x30000);
        kfree(dest);
        return 0;

}

static void __exit kernmem_exit(void)
{
   printk(KERN_ALERT "Good Bye World\n");
}

module_init(kernmem_init);
module_exit(kernmem_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("CW");
MODULE_DESCRIPTION("Demo Hello");
