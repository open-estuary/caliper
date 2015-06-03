
build_nbench()
{
    set -e

    SrcPath=${BENCH_PATH}"405.nbench"
    myOBJPATH=${INSTALL_DIR}/nbench
    pushd $SrcPath
    mkdir -p $myOBJPATH
    if [ $ARCH = "x86_64" -o $ARCH = "x86_32" ];then
         make     
         cp * $myOBJPATH
         make CC=$GCC clean     
    fi
    if [ $ARCH = "arm_32" ]; then
        make CC=$GCC CFLAGS="-mfloat-abi=hard -mfpu=vfpv4 -mcpu=cortex-a15"     
        cp * $myOBJPATH
        make CC=$GCC clean     
    fi
    if [ $ARCH = "arm_64" ]; then
        make CC=$GCC      #CFLAGS="-mabi=lp64"
        cp * $myOBJPATH
        make CC=$GCC clean     
    fi
    if [ $ARCH = "android" ]; then
        ndk-build     
        cp libs/armeabi-v7a/nbench $myOBJPATH
        ndk-build clean     
        rm -fr lib/ obj/
    fi
    popd
}

build_nbench
