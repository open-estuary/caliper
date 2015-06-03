build_memspeed() {
    set -e

        SrcPath=${BENCH_PATH}"412.memspeed"
   myOBJPATH=${INSTALL_DIR}/bin
        pushd $SrcPath
        if  [ $ARCH = "x86_64" -o $ARCH = "x86_32" ]; then
                make CC=$GCC CFLAGS="-msse4"    
           mv memspeed    $myOBJPATH
        fi
        if [ $ARCH = "arm_64" -o $ARCH = "arm_32" ]; then
            #if [ $ARCH = "arm_64" ]; then
             #   CFLAGS_OPT="-mabi=lp64"
            #else
            if [ $ARCH = "arm_32" ]; then
                make CC=$GCC CFLAGS="-mfloat-abi=hard -mfpu=vfpv4 -mcpu=cortex-a15"    
               mv  memspeed    $myOBJPATH
            fi
        fi
        if [ $ARCH = "android" ]; then
                ndk-build    
                cp libs/armeabi-v7a/memspeed $myOBJPATH
                ndk-build clean
                rm -rf libs/ obj
        fi
        popd
}

build_memspeed
