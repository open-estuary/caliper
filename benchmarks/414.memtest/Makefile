#VERSION = 3
#PATCHLEVEL = 2
#SUBLEVEL = 0
#EXTRAVERSION = 00763-g4071679


obj-m := kern_mem.o
#KDIR := /lib/modules/$(shell uname -r)/build
ODIR := /home/m00177601/k3v3/out/target/product/hi3630/obj/KERNEL_OBJ
KDIR := /home/m00177601/k3v3/kernel
PWD := $(shell pwd)

default:
   $(MAKE) ARCH=arm CROSS_COMPILE=/home/m00177601/k3v3/prebuilts/gcc/linux-x86/arm/arm-eabi-4.7/bin/arm-eabi- -C $(KDIR) O=${ODIR}  SUBDIRS=$(PWD) modules

clean:
   $(MAKE) -C $(KDIR) SUBDIRS=$(PWD) clean
