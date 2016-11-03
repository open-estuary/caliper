#!/bin/bash 
set -x
download_dir=$HOME/.caliper
if [ ! -f $download_dir ]; then
    mkdir -p $download_dir
fi
checksum_result=1 # Default download is needed , if exising file is proper rewrite checksum_result=0
check_sum()
{
    checksum_source=$1
    md5_file=$2
    if [ x"$checksum_source" = x"" ]; then 
        echo "Please check the download file name"
        checksum_result=1
        exit 1
    fi

    if [ x"$md5_file" = x"" ]; then 
        echo "Please check the md5sum file name"
        checksum_result=1
        exit 1
    fi

    md5_value=$(cat $md5_file)
    check_value=$(md5sum $checksum_source | awk '{print $1}')
    if [ x"$md5_value" != x"$check_value" ]; then
        checksum_result=1
        echo "The files are not downloaded properly, checksum error"
    else
        checksum_result=0
        echo "Downloaded $checksum_source successfully"
    fi
}

download_file()
{
    # we have less than 3 arguments. Print the help text:
    checksum_result=1
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
#fixme check the url is reachable or not
    pushd $file_store_location
    # Download firstly
    echo "Check the checksum for $file ..."

    # always delete and then update the md5sum file
    
    if [ -f $sum_file ]; then
    rm $sum_file
    fi

    wget $download_sum_file 2>/dev/null
 
    if [ $? -ne 0 ]; then
        echo "Download the $download_sum_file failed"
        exit 1
    fi

    if [ -f $file ]; then
	check_sum $file $sum_file
	
	if [ $checksum_result -ne 0 ]; then
		echo "Existing file checksum failed. Downloading the file : $file again ..."
		rm $file
	
	fi
    fi
 # checksum_result =1 means either the existing file checksum is not ok or the file is not there.   
  if [ $checksum_result -ne 0 ]; then
    wget $download_file 2>/dev/null
    if [ $? -ne 0 ]; then
	echo "Downloading a fresh copy of file : $file is failed "
	exit 1
    else
         check_sum $file $sum_file
    	 if [ $checksum_result -ne 0 ]; then
        	 echo " Check the connectivity, Checksum is not matching for the freshly downloaded file"
		 exit 1
	 else	
	       echo " The file has been updated and checksum found to be ok. "	
         fi 
    fi
  fi
    
    popd
}

build_prepare() {
    
    OBJPATH=$OBJDIR/$ARCH
    BENCH_PATH="benchmarks/"

    caliper_exists=$(which caliper)
    if [ "$caliper_exists"x != ""x ]; then
        INSTALL_DIR="$HOME/caliper_output/$OBJPATH"
        BENCH_PATH=$TMP_DIR/$BENCH_PATH
        CURRENT_PATH=""
    else
        INSTALL_DIR="$MYPWD/caliper_output/$OBJPATH"
        CURRENT_PATH=$MYPWD
    fi

    OBJPATH=$TMP_DIR/$OBJPATH
    #BENCH_PATH=$TMP_DIR/$BENCH_PATH

    #if [ ! -d $OBJPATH/bin ]; then
    #    mkdir -p $OBJPATH/bin
    #fi
    if [ ! -d $INSTALL_DIR ]; then
        mkdir -p $INSTALL_DIR
    fi
    if [ ! -d $INSTALL_DIR/bin ]; then
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

OBJDIR=$4
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
CALIPER_TMP=$TMP_DIR

build_prepare

start=$(date +%s)
