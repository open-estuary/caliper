build_powerMgr()
{
    set -e
   SrcPath=${BENCH_PATH}"301.powerMgr"
    if [ $ARCH = "x86_64" -o $ARCH = "x86_32" ]
   then
      pushd $SrcPath
      make     
      popd
      cp $SrcPath ${OBJPATH}/powerMgr -rf
      pushd $SrcPath
      make clean     
      popd
   fi

        if [ $ARCH = "arm_64" -o $ARCH = "arm_32" ]
        then
                pushd $SrcPath
                make CC=$GCC     
                popd
                cp $SrcPath ${OBJPATH}/powerMgr -rf
                pushd $SrcPath
                make clean     
                popd
        fi

        if [ $ARCH = "android" ]
        then
      myARMCROSS=arm-linux-gnueabihf
                pushd $SrcPath
                make CC="${myARMCROSS}-gcc --static"     
                popd
                cp $SrcPath ${OBJPATH}/powerMgr -rf
                pushd $SrcPath
                make clean     
                popd
        fi
}

build_powerMgr
