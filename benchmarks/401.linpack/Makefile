CC ?= gcc
CFLAGS ?= -O2

linpack.o:linpack.c
	${CC} ${CFLAGS} -DSP -c -o linpack_sp.o linpack.c
	${CC} ${CFLAGS} -DDP -c -o linpack_dp.c linpack.c

linpack:linpack.o
	${CC} -O2 ${LDFLAGS} -o linpack_sp linpack_sp.o
	${CC} -O2 ${LDFLAGS} -o linpack_dp linpack_dp.o

clean:
	rm -rf *.o linpack_sp linpack_dp
