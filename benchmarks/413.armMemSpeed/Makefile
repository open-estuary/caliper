CC = arm-linux-gnueabihf-gcc
CFLAGS = -g -O3 -Wall -fno-tree-vectorize
ASFLAGS = $(CFLAGS)
LDFLAGS = -static

ALL = memspeed_a8 memspeed_a9 memspeed_a9d16

all: $(ALL)

memspeed_a8:    CFLAGS  += -mcpu=cortex-a8 -mfpu=neon -DPLE_A8
memspeed_a9:    CFLAGS  += -mcpu=cortex-a9 -mfpu=neon
memspeed_a9d16: CFLAGS  += -mcpu=cortex-a9 -mfpu=vfpv3-d16 -D__ARM_NEON__

memspeed_%.o: memspeed.c
   $(CC) $(CFLAGS) -c -o $@ $^

memspeed_%: memspeed_%.o mem.o memcpy_androidv5.o memcpy_androidv7.o memcpy_a9.o
   $(CC) $(LDFLAGS) -o $@ $^

clean:
   rm -f $(ALL) *.o
