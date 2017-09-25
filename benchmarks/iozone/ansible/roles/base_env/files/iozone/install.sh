build_iozone() {    
    set -e
    ARCH=`uname -i`
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
    SrcPath=$(cd `dirname $0`; pwd)
    mkdir -p /dev/sdb
    mkdir -p /mnt/sdb
    chmod -R 775 /mnt/sdb
    chown -R root:root /mnt/sdb
    mount /dev/sdb /mnt/sdb
    myOBJPATH=/mnt/sdb/
    pushd $SrcPath
    if [ $ARCH = "x86_64" ]
    then
        make linux-AMD64 -s
        cp iozone $myOBJPATH
        cp fileop $myOBJPATH
        make clean
    fi
    if [ $ARCH = "x86_32" ]; then
        make linux -s
        cp iozone $myOBJPATH
        cp fileop $myOBJPATH
        make clean
    fi
    if [ $ARCH = "arm_64" -o $ARCH = "arm_32" ]
    then
        make linux-arm CC=$GCC GCC=$GCC -s
        cp iozone $myOBJPATH
        cp fileop $myOBJPATH
        make clean
    fi
    popd
}

build_iozone
