#!/bin/bash

build_compile() {
   set -e
   set -x
   Path=$BENCH_PATH"312.unzip"
   myOBJPATH=${INSTALL_DIR}/scripts
   if [ ! -d $myOBJPATH ]; then
        mkdir -p $myOBJPATH
   fi
       if [ ! -f $myOBJPATH/kernel-dev.tar.gz ]; then
           cp $BENCH_PATH"311.compile/kernel-dev.tar.gz" $myOBJPATH
       fi
       cp $Path/* $myOBJPATH
}

build_compile

