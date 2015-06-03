CC=arm-linux-androideabi-gcc
AndroidPath=/home/m00177601/k3v3
BoardPath=${AndroidPath}/out/target/product/hi3630

TARGET_ARCH  := arm
libc_root := ${AndroidPath}/bionic/libc
libm_root := ${AndroidPath}/bionic/libm
libstdc++_root   := ${AndroidPath}/bionic/libstdc++
libthread_db_root   := ${AndroidPath}/bionic/libthread_db
KERNEL_HEADERS_COMMON   := $(libc_root)/kernel/common
KERNEL_HEADERS_ARCH := $(libc_root)/kernel/arch-$(TARGET_ARCH)
TARGET_C_INCLUDES := \
        -I$(libc_root)/arch-arm/include \
        -I$(libc_root)/include \
        -I$(libstdc++_root)/include \
   -I$(KERNEL_HEADERS_COMMON) \
   -I$(KERNEL_HEADERS_ARCH) \
        -I$(libm_root)/include \
        -I$(libm_root)/include/arm \
        -I$(libthread_db_root)/include

CFLAGS := -O2 -mfloat-abi=softfp -mfpu=neon-vfpv4 -march=armv7-a

LDFLAGS = -nostdlib ${BoardPath}/obj/lib/crtbegin_dynamic.o ${BoardPath}/obj/lib/crtend_android.o  -L${BoardPath}/system/lib -lc -lm

all: memread

memread.o:
   ${CC} -Ilinux -I. ${TARGET_C_INCLUDES}  ${CFLAGS} -c -o memread.o memread.c
bsp_memcpy.o:
   ${CC} -Ilinux -I. ${TARGET_C_INCLUDES}  ${CFLAGS} -c -o bsp_memcpy.o bsp_memcpy.S
  
  
memread: memread.o bsp_memcpy.o
   ${CC} -O2 ${LDFLAGS}  -o memread memread.o bsp_memcpy.o
   @rm -rf *.o

clean:
   rm -rf *.o memread
