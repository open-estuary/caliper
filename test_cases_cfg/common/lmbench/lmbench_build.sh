build_lmbench() {
    set -e

        SrcPath="${BENCH_PATH}490.lmbench"
        pushd $SrcPath

        myOBJPATH="${INSTALL_DIR}/lmbench"
        mkdir -p $myOBJPATH
        mkdir -p $myOBJPATH/src
        mkdir -p $myOBJPATH/results
        cp -r -f scripts  $myOBJPATH
        cp src/webpage-lm.tar $myOBJPATH/src
        cp -f CONFIG lmbench_latency lmbench_bandwidth test.sh test_local_bw.sh test_cross_bw.sh test_lat.sh $myOBJPATH
    make clean
   if [ $ARCH = "x86_64" -o $ARCH = "x86_32" ]; then
      make OS=lmbench  CC="$GCC -O2 -msse4" -s
   fi
   if [ $ARCH = "arm_64" -o $ARCH = "arm_32" ]; then
        if [ $ARCH = "arm_32" ]; then
          make OS=lmbench  CC="$GCC -mfloat-abi=hard -mfpu=vfpv4 -mcpu=cortex-a15"   
         else
          make OS=lmbench  CC=$GCC        # " -mabi=lp64" 
         fi
   fi
    if [ $ARCH = "android" ]; then
        myARMCROSS=arm-linux-gnueabihf
                myGCC=${myARMCROSS}-gcc
        make OS=lmbench  CC="$myGCC --static -mfloat-abi=hard -mfpu=neon-vfpv4 -mcpu=cortex-a15"
        #make -f makefile.android CROSS_COMPILE=$ANDROIDCROSS SYSROOT=$ANDROIDSYSROOT
        #cp bin/* ../$OBJPATH/lmbench/ -rf
    fi
    mv bin/lmbench/*  $myOBJPATH
    rm -rf bin
    if [ -f "$myOBIPATH/lmbench" ]; then
        sed -i 's/\.\.\/\.\.\//\.\//g' "$myOBJPATH/lmbench"
    fi
    cd $myOBJPATH/../
    tar -cvf lmbench_tar.gz lmbench
    rm -fr lmbench
    popd
}

build_lmbench
