build_iperf() {
    set -e
       SrcPath=${BENCH_PATH}"420.iperf"
        BuildPATH="$CALIPER_TMP/build.iperf"
        TOP_SRCDIR="$CURRENT_PATH/$SrcPath"
   myOBJPATH=${INSTALL_DIR}/bin
   mkdir -p $BuildPATH

        if [ $ARCH = "x86_64" -o $ARCH = "x86_32" ]
        then
      pushd $BuildPATH
                $TOP_SRCDIR/configure --disable-shared --enable-static --prefix=$BuildPATH                      
                make
		make install
		cp bin/iperf3 $myOBJPATH
      popd
      rm -rf $BuildPATH
        fi

        if [ $ARCH = "arm_64" -o $ARCH = "arm_32" ]
        then
            #echo ${GCC//gcc/g++}
      pushd $BuildPATH
             export ac_cv_func_malloc_0_nonnull=yes 
             $TOP_SRCDIR/configure --disable-shared --enable-static --prefix=$BuildPATH --host=$ARMCROSS  CC=$GCC CXX=${GCC//gcc/g++}      
                make
		make install
		cp bin/iperf3 $myOBJPATH
      popd
      rm -rf $BuildPATH
        fi

        if [ $ARCH = "android" ]; then
            pushd $BuildPATH
            cp $TOP_SRCDIR/* ./ -rf
            cp include/config.android.h include/config.h
            cp include/iperf-int.android.h include/iperf-int.h
            ndk-build V=1 LOCAL_DISABLE_FORMAT_STRING_CHECKS=true     
            cp ./libs/armeabi-v7a/iperf3 $myOBJPATH
            popd
            rm -rf $BuildPATH
        fi
}

build_iperf
