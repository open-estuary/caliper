#!/usr/bin/env bash
build_unixbench() {
   set -e
   CoreMarkPath=$BENCH_PATH"501.byte-unixbench"
   myOBJPATH="$INSTALL_DIR/unixbench"
   if [ ! -d $myOBJPATH ]
   then
       mkdir -p $myOBJPATH
   fi
   pushd $CoreMarkPath
   if [ $ARCH = "arm_64" -o $ARCH = "arm_32" ]
   then
	    make CC=$GCC
   else
        make
   fi
	cp -r $CoreMarkPath/* $myOBJPATH
	make clean
   popd

}

build_unixbench
