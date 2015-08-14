build_netperf() {
    set -e
        SrcPath=${BENCH_PATH}"421.netperf"
        BuildPATH="$CALIPER_TMP/build.netperf"
        TOP_SRCDIR="$CURRENT_PATH/$SrcPath"
        myOBJPATH=${INSTALL_DIR}/bin

        if [ $ARCH = "x86_64" -o  $ARCH = "x86_32" ]
        then
      mkdir -p $BuildPATH
      pushd $BuildPATH
      cp $TOP_SRCDIR/* ./ -rf
                aclocal -I src/missing/m4
                automake  --add-missing     
                autoconf      
                autoheader      
                ./configure      
                make      
                cp src/netperf $myOBJPATH
                cp src/netserver $myOBJPATH
      popd
      rm -rf $BuildPATH
        fi

        if [ $ARCH = "arm_64" -o $ARCH = "arm_32" ]
        then
      mkdir -p $BuildPATH
      pushd $BuildPATH
      cp $TOP_SRCDIR/* ./ -rf
                aclocal -I src/missing/m4
                automake  --add-missing      
                autoconf      
                autoheader      
                ac_cv_func_setpgrp_void=yes ac_cv_func_malloc_0_nonnull=yes ./configure      #--host=$ARMCROSS
           make CC=$GCC
           cp src/netperf $myOBJPATH
           cp src/netserver $myOBJPATH
      popd
      rm -rf $BuildPATH
        fi
}

build_netperf
