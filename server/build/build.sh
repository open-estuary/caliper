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
    if [ ! -d $OBJPATH/bin ]; then
       mkdir -p $OBJPATH/bin
    fi
    #if [! -d $OBJDIR/output ]; then
    #    mkdir -p $OBJDIR/output
    #    cp -r server/parser_process/show_output/output/ $OBJPATH
    #fi
   
# SPV - for adding time stamp to the temp folder so that caliper can run on multiple board simultaneously
    NOW=$(date +"%Y-%m-%d_%H-%M-%S") 
    CALIPER_TMP="/tmp/caliper_$NOW.tmp"
    if [ ! -d $CALIPER_TMP ]; then
        mkdir -p $CALIPER_TMP
    fi
    
    INSTALL_DIR="$MYPWD/$OBJPATH"
    LOG_FILE="$CALIPER_BUILD/build.log"
}

#build_bench_cleanup()
#{
#    bench_name=$1
#    bench_name=$(echo $bench_name | awk -F '_' '{print $2}')
#    build_result=$2
#
#    end=$(date +%s)
#
#    interval=$(( $end - $start ))
#
#    if [ $build_result -eq 0 ]
#    then
#        do_msg_end "$bench_name build successfully"
#        if [ ! -d $CALIPER_BUILD ]; then
#            mkdir -p $CALIPER_BUILD
#        fi
#        success_file="$CALIPER_BUILD/${bench_name}_${ARCH}.successfully"
#        mv $LOG_FILE $success_file
#    else
#        do_msg_end "$bench_name build failed"
#        if [ -d $CALIPER_BUILD ]; then
#            mkdir -p $CALIPER_BUILD
#        fi
#        failed_file="$CALIPER_BUILD/${bench_name}_${ARCH}.failed"
#        mv $LOG_FILE $failed_file
#    fi
#}

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

BENCH_PATH="benchmarks/"

start=$(date +%s)

#build_cleanup
