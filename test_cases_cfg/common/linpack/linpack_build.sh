build_linpack() {
    set -e

        SrcPath=$BENCH_PATH"401.linpack"
   myOBJPATH=${INSTALL_DIR}/bin
        pushd $SrcPath
        if [ $ARCH = "android" ]; then
      ndk-build     
      cp libs/armeabi-v7a/linpack_sp  $myOBJPATH/
      cp libs/armeabi-v7a/linpack_dp  $myOBJPATH/
      ndk-build clean
      rm -rf libs/ obj/
   else
      ${GCC} -O2  -DDP -o linpack_dp linpack.c     
      ${GCC} -O2 -DSP -o linpack_sp linpack.c     
           mv linpack_sp $myOBJPATH/
           mv linpack_dp $myOBJPATH/
        fi     
        popd

}

build_linpack
