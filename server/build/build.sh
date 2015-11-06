#!/bin/bash 

download_dir=$HOME/.caliper
if [ ! -f $download_dir ]; then
    mkdir -p $download_dir
fi
checksum_result=0
check_sum()
{
    checksum_source=$1
    md5_file=$2
    if [ x"$checksum_source" = x"" ]; then 
        echo "Invalidate file!"
        checksum_result=1
        exit 1
    fi   
    
    md5_value=$(cat $md5_file)
    check_value=$(md5sum $checksum_source | awk '{print $1}')
    if [ x"$md5_value" != x"$check_value" ]; then
        checksum_result=1
        echo 'The download files error'
        exit 1
    else
        checksum=0
        echo "Download $checksum_source successfully"
    fi
}

download_file()
{
    # we have less than 3 arguments. Print the help text:
    if [ $# -lt 3 ] ; then
        echo 
        'download.sh  -- download and check if the package downloads correctly
        USAGE: download.sh "location" "url_head" "packages"
        EXAMPLE: download pack from url_head and put it in Location:
        　download.sh "location" "url_head" "pack"'
        　exit 0
    fi

    file_store_location=$1
    url_head=$2
    file=$3
    sum_file="$file".md5sum

    download_file=$url_head/$file
    download_sum_file="$download_file".md5sum

    pushd $file_store_location
    # Download firstly
    echo "Check the checksum for $file ..."

    # always update the md5sum file
    wget -c $download_sum_file 2>/dev/null
    if [ $? -ne 0 ]; then 
        echo "Download the $download_sum_file failed"
        exit 1
    fi

    if [ ! -f $file ]; then 
        wget -c $download_file 2>/dev/null
        if [ $? -ne 0 ]; then 
            echo "Download the $download_file failed"
            exit 1
        fi
    fi

    check_sum $file $sum_file
    if [ $checksum_result -ne 0 ]; then 
        echo "Download the $file ..."
        wget -c $download_file 2>/dev/null
        if [ $? -ne 0 ]; then 
            rm -rf $file $sum_file 2>/dev/null
            echo "Download $file failed!"
            exit 1
        fi
    fi
    popd
}

build_prepare() {
    
    OBJPATH=$OBJDIR/$ARCH
    BENCH_PATH="benchmarks/"
    
    caliper_exists=$(which caliper)
    if [ "$caliper_exists"x != ""x ]; then
        INSTALL_DIR="/home/$(whoami)/caliper_workspace/$OBJPATH"
        CURRENT_PATH=""
    else
        INSTALL_DIR="$MYPWD/caliper_workspace/$OBJPATH"
        CURRENT_PATH=$MYPWD
    fi

    OBJPATH=$TMP_DIR/caliper_build/$OBJPATH
    BENCH_PATH=$TMP_DIR/caliper_build/$BENCH_PATH
    
    if [ ! -d $OBJPATH/bin ]; then
         mkdir -p $OBJPATH/bin
    fi
    if [ ! -d $INSTALL_DIR ]; then
         mkdir -p $INSTALL_DIR
         mkdir -p $INSTALL_DIR/bin
    fi
    
}

build_cleanup()
{
    BIN_PATH=$OBJPATH/bin
    if [ "`ls -A $BIN_PATH`" = "" ]; then
        rm -fr $BIN_PATH
    fi
}

OBJDIR=binary
TMP_DIR=$3
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

