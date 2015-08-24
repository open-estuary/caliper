#!/bin/bash

build_scimarkJava() {
   set -e

   Path=$BENCH_PATH"321.scimarkJava"
   myOBJPATH=${INSTALL_DIR}/scimarkJava

   if [ ! -d $myOBJPATH ]; then
       mkdir -p $myOBJPATH
   fi

   pushd $Path
    cp * $myOBJPATH
   popd

}

build_scimarkJava

