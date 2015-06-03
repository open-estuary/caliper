build_iozone() {    
    set -e
       SrcPath=${BENCH_PATH}"430.iozone"
   myOBJPATH=${INSTALL_DIR}/bin

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

        if [ $ARCH = "android" ]
        then
      myARMCROSS=arm-linux-gnueabihf
                make linux-arm CC=$myARMCROSS-gcc GCC=$myARMCROSS-gcc LDFLAGS="--static"    
      $myARMCROSS-strip iozone
      $myARMCROSS-strip fileop
                cp iozone $myOBJPATH
                cp fileop $myOBJPATH
                make clean     
        fi
        popd
}

build_iozone
