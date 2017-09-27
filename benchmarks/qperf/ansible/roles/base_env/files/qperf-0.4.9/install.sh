build_scimark() {
    set -e
    ARCH=`uname -i`
    if [ $ARCH = "aarch32" ]; then
        ARMCROSS=arm-linux-gnueabihf
        GCC=${ARMCROSS}-gcc
        STRIP=${ARMCROSS}-strip
    elif [ $ARCH = "aarch64" ]; then
        ARMCROSS=aarch64-linux-gnu
        GCC=${ARMCROSS}-gcc
        STRIP=${ARMCROSS}-strip
    fi

    if [ $ARCH = "x86_64" -o $ARCH = "x86_32" ]; then
        GCC=gcc
        STRIP=strip
    fi
    SrcPath=$(cd `dirname $0`; pwd)
    myOBJPATH=/usr/bin
    pushd $SrcPath
    if [ $ARCH = "x86_32" -o $ARCH = "x86_64" ]; then
        make CC=$GCC CFLAGS="-msse4"
    fi
    if [ $ARCH = "aarch32" ]; then
        # -mfloat-abi=hard -mfpu=vfpv4 -mcpu=cortex-a15
        make CC=$GCC CFLAGS=" -mfloat-abi=hard -mfpu=vfpv4 -mcpu=cortex-a15 "
    fi
    if [ $ARCH = "aarch64" ]; then
        make CC=$GCC      #CFLAGS="-mabi=lp64"
    fi
    popd
}

build_scimark
