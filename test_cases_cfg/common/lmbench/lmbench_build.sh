build_lmbench() {
    set -e
set -x
        SrcPath="${BENCH_PATH}490.lmbench"
        pushd $SrcPath

        myOBJPATH="${INSTALL_DIR}/lmbench"
        mkdir -p $myOBJPATH
        mkdir -p $myOBJPATH/src
        mkdir -p $myOBJPATH/results
        cp -r -f scripts  $myOBJPATH
        cp src/webpage-lm.tar $myOBJPATH/src
        cp -f CONFIG lmbench_latency lmbench_bandwidth test.sh $myOBJPATH

   if [ $ARCH = "x86_64" -o $ARCH = "x86_32" ]; then
      make OS=lmbench  CC="$GCC -O2 -msse4" -s     
           mv bin/lmbench/*  $myOBJPATH
           rm -rf bin
   fi
   if [ $ARCH = "arm_64" -o $ARCH = "arm_32" ]; then
        if [ $ARCH = "arm_32" ]; then
          make OS=lmbench  CC="$GCC -mfloat-abi=hard -mfpu=vfpv4 -mcpu=cortex-a15"   
         else
          make OS=lmbench  CC=$GCC        # " -mabi=lp64" 
         fi
                mv bin/lmbench/*    $myOBJPATH 
                rm -rf bin
   fi
    if [ $ARCH = "android" ]; then
        myARMCROSS=arm-linux-gnueabihf
                myGCC=${myARMCROSS}-gcc
        make OS=lmbench  CC="$myGCC --static -mfloat-abi=hard -mfpu=neon-vfpv4 -mcpu=cortex-a15"    
        mv bin/lmbench/*    $myOBJPATH
        rm -rf bin
        #make -f makefile.android CROSS_COMPILE=$ANDROIDCROSS SYSROOT=$ANDROIDSYSROOT
        #cp bin/* ../$OBJPATH/lmbench/ -rf
    fi

    if [ -f "$myOBIPATH/lmbench" ]; then
        sed -i 's/\.\.\/\.\.\//\.\//g' "$myOBJPATH/lmbench"
    fi
    popd
}

build_lmbench
