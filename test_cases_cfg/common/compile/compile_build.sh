#!/bin/bash

build_compile() {

    set -x
    set -e

   Path=$BENCH_PATH"311.compile"
   myOBJPATH=${INSTALL_DIR}/scripts

   if [ ! -d $myOBJPATH ]; then
       mkdir -p $myOBJPATH
   fi

   pushd $Path
    if [ ! -f $myOBJPATH/kernel-dev.tar.gz ]; then
        cp kernel-dev.tar.gz $myOBJPATH
    fi
    cp *.sh $myOBJPATH
   popd

}

build_compile

