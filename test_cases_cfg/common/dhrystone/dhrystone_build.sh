build_dhrystone()
{
    set -e

    SrcPath=${BENCH_PATH}'404.dhrystone'
    myOBJPATH=${INSTALL_DIR}/bin
    pushd $SrcPath
    if [ $ARCH = "x86_64" ]; then
        make GCC=gcc unix
        cp gcc_dry2 $myOBJPATH
    fi
    if [ $ARCH = "arm_64" ]; then
        make GCC=aarch64-linux-gnu-gcc unix
        cp gcc_dry2 $myOBJPATH
    fi
    popd
}

build_dhrystone

