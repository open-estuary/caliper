build_cachebench() {
    set -e

        SrcPath=${BENCH_PATH}"410.cachebench"
   myOBJPATH=${INSTALL_DIR}/bin
        pushd $SrcPath
        if [ $ARCH = "x86_32" -o $ARCH = "x86_64" ]; then
      make CC=$GCC CFLAGS="-msse4" -s     
           mv cachebench    $myOBJPATH
        fi
        if [ $ARCH = "arm_32" ]; then
          make CC=$GCC CFLAGS="-mfloat-abi=hard -mfpu=vfpv4 -mcpu=cortex-a15" -s     
           mv cachebench    $myOBJPATH
        fi
        if [ $ARCH = "arm_64" ]; then
          make CC=$GCC -s       #CFLAGS="-mabi=lp64"
           mv cachebench    $myOBJPATH
        fi
        if [ $ARCH = "android" ]; then
      ndk-build     
      cp libs/armeabi-v7a/cachebench $myOBJPATH
      ndk-build clean
      rm -rf libs/ obj/
        fi
        popd
}

build_cachebench

