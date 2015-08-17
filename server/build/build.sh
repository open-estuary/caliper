#!/bin/bash
# wu.wu@hisilicon.com
#

do_msg() {
   OBJ=$1
   ACTION=$2
   echo "========================================================="
   echo "$OBJ  $ACTION"
}

do_msg_end()
{
    OBJ=$1
   ACTION=$2
   echo "$OBJ  $ACTION"
   echo "========================================================="
   
}

build_prepare() {
    OBJPATH=$OBJDIR/$ARCH
       BENCH_PATH="benchmarks/"
    caliper_exists=$(which caliper)

    if [ "$caliper_exists"x != ""x ]; then
        INSTALL_DIR="/home/$(whoami)/.caliper/$OBJPATH"
        OBJPATH=/tmp/caliper_build/$OBJPATH
        BENCH_PATH=/tmp/caliper_build/$BENCH_PATH
        CURRENT_PATH=""
    else
        INSTALL_DIR="$MYPWD/$OBJPATH"
        CURRENT_PATH=$MYPWD
    fi
        if [ ! -d $OBJPATH/bin ]; then
            mkdir -p $OBJPATH/bin
        fi
        if [ ! -d $INSTALL_DIR ]; then
            mkdir -p $INSTALL_DIR
            mkdir -p $INSTALL_DIR/bin
        fi

# SPV - for adding time stamp to the temp folder so that caliper can run on multiple board simultaneously
    NOW=$(date +"%Y-%m-%d_%H-%M-%S") 
    CALIPER_TMP="/tmp/caliper_$NOW.tmp"
    if [ ! -d $CALIPER_TMP ]; then
        mkdir -p $CALIPER_TMP
    fi

    #LOG_FILE="$CALIPER_BUILD/build.log"
}

build_cleanup()
{
    BIN_PATH=$OBJPATH/bin
    if [ "`ls -A $BIN_PATH`" = "" ]; then
        rm -fr $BIN_PATH
    fi
}

OBJDIR=binary
if [ $# -eq 0 ]; then
   ARCH=x86_64
else
   ARCH=$1
fi
if [ $ARCH = "arm_32" ]; then
   ARMCROSS=arm-linux-gnueabihf
   GCC=${ARMCROSS}-gcc
   STRIP=${ARMCROSS}-strip
elif [ $ARCH = "arm_64" ]; then
   ARMCROSS=aarch64-linux-gnu
   GCC=${ARMCROSS}-gcc
   STRIP=${ARMCROSS}-strip
fi

if [ $ARCH = "x86_64" -o $ARCH = "x86_32" ]; then
   GCC=gcc
   STRIP=strip
fi
if [ $ARCH = "android" ]; then
   #ANDROID_NDK_PATH=/opt/android-ndk-r9d
   ANDROID_SDK_PATH=/opt/android-sdk-linux
   # for dx command usage, converting jar package into dex package
   export PATH=$PATH:$ANDROID_SDK_PATH/build-tools/19.1.0
 ANDROIDCROSS=$ANDROID_NDK_PATH/toolchains/arm-linux-androideabi-4.8/prebuilt/linux-x86/bin/arm-linux-androideabi-
   ANDROIDGCC=${ANDROIDCROSS}gcc
   ANDROIDSYSROOT=$ANDROID_NDK_PATH/platforms/android-19/arch-arm
fi

MYPWD=$2

build_prepare


start=$(date +%s)

