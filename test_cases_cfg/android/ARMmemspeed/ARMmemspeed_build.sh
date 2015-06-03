build_ARMmemspeed() {
    set -e

        SrcPath=${BENCH_PATH}"413.armMemSpeed"
   myOBJPATH=${INSTALL_DIR}/bin
        pushd $SrcPath
        if [ $ARCH = "arm_32" -o $ARCH = "arm_64" ]; then
            #if [ $ARCH = "arm_64" ]; then
            #    CFLAGS_OPT="-mabi=lp64"
            #else
            if [ $ARCH = "arm_32" ]; then
            make CC=$GCC CFLAGS="-mfloat-abi=hard -mfpu=vfpv4 -mcpu=cortex-a15 -g -O3 -Wall -fno-tree-vectorize"    
           mv memspeed_a8    $myOBJPATH/
           mv memspeed_a9    $myOBJPATH/
           mv memspeed_a9d16 $myOBJPATH/
            fi
        fi
        if [ $ARCH = "android" ]; then
            make CC="$ANDROIDGCC --sysroot=$ANDROIDSYSROOT" CFLAGS="-mfloat-abi=soft -mfpu=neon-vfpv4 -mcpu=cortex-a15 -g -O3 -Wall -fno-tree-vectorize"     
            mv memspeed_a8    $myOBJPATH/
            mv memspeed_a9    $myOBJPATH/
            mv memspeed_a9d16 $myOBJPATH/
        fi
        popd
}

build_ARMmemspeed
