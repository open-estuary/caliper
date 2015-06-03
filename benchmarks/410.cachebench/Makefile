
CC ?= gcc
CFLAGS ?= -O2

cachebench:cachebench.c
	${CC} ${CFLAGS} -Wall -DREGISTER -DUSE_DOUBLE cachebench.c -o cachebench

clean:
	rm -rf cachebench
