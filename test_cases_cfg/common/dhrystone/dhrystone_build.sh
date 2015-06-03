build_dhrystone()
{
    set -e

    SrcPath=${BENCH_PATH}'404.dhrystone/source_code'
    myOBJPATH=${INSTALL_DIR}/bin
    pushd $SrcPath
    if [ $ARCH = "x86_64" ]; then
        make CC=$GCC CFLAGS="-O3 -Icommon_64bit -lrt -lm" -s     
        cp dhry1 dhry2 lloops whets $myOBJPATH
        make CC=$GCC clean     
    fi
    if [ $ARCH = "x86_32" ]; then
        make CC=$GCC CFLAGS="-O3 -Icommon_32bit -lrt -lm" -s     
        cp dhry1 dhry2 lloops whets $myOBJPATH
    fi
    if [ $ARCH = "arm_32" ]; then
        #-mcpu=cortex-a15 -mtune=cortex-a15 -mfpu=neon -funroll-loops 
        make CC=$GCC CFLAGS="-static -O3 -Icommon_32bit -lrt -lm" -s     
        cp dhry1 dhry2 lloops whets $myOBJPATH
        make CC=$GCC clean     
    fi
    if [ $ARCH = "arm_64" ]; then
        make CC=$GCC CFLAGS="-static -O3 -funroll-loops -Icommon_64bit -lrt -lm" -s     
        cp dhry1 dhry2 lloops whets $myOBJPATH
        make CC=$GCC clean     
    fi
    if [ $ARCH = "android" ]; then
        ndk-build     
        cp libs/armeabi-v7a/scimark2 $myOBJPATH
        ndk-build clean
        rm -fr lib/ obj/
    fi
    popd
}

build_dhrystone

