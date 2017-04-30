build_qperf() {
        set -e
        SrcPath=${BENCH_PATH}"503.qperf"
        BuildPATH="$CALIPER_TMP/build.qperf"
        TOP_SRCDIR="$CURRENT_PATH/$SrcPath"
        myOBJPATH=${INSTALL_DIR}/bin
        mkdir -p $BuildPATH

        if [ $ARCH = "x86_64" -o $ARCH = "x86_32" ]
        then
                pushd $BuildPATH
                $TOP_SRCDIR/configure --prefix=$BuildPATH
                make
                cp src/qperf $myOBJPATH
                popd
                rm -rf $BuildPATH
        fi

        if [ $ARCH = "arm_64" -o $ARCH = "arm_32" ]
        then
                pushd $BuildPATH
                export ac_cv_func_malloc_0_nonnull=yes 
                $TOP_SRCDIR/configure --disable-shared --enable-static --prefix=$BuildPATH --host=$ARMCROSS  CC=$GCC CXX=${GCC//gcc/g++}
                make
                cp src/qperf $myOBJPATH
                popd
                rm -rf $BuildPATH
        fi
}

build_qperf


