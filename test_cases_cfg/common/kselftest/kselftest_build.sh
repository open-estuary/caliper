build_kselftest() {
    set -e

    SrcPath=$BENCH_PATH"301.kselftest"
    myOBJPATH=${INSTALL_DIR}/kselftest
    mkdir -p $myOBJPATH

    pushd $SrcPath
    if [ $ARCH = "android" ]; then
        ndk-build
        cp libs/armeabi-v7a/linpack_sp  $myOBJPATH/
        cp libs/armeabi-v7a/linpack_dp  $myOBJPATH/
        ndk-build clean
        rm -rf libs/ obj/
    else
        make CC=$GCC
        cp -r * $myOBJPATH/
        cd $myOBJPATH/../
        tar -cvf kselftest.tar.gz kselftest
        rm -fr kselftest
        make clean
    fi
    make clean
    popd

}

build_kselftest
