
build_busybox()
{
    set -e
        SrcPath=${BENCH_PATH}"491.busybox"
   myOBJPATH=${INSTALL_DIR}/bin
   mkdir -p $myOBJPATH
        if [ $ARCH = "x86_64" -o $ARCH = "x86_32" ]
            then
                    pushd $SrcPath
                    make defconfig       
                    make -s      
                    cp -r busybox $myOBJPATH
            make distclean     
                    popd
        fi

        if [ $ARCH = "arm_64" -o $ARCH = "arm_32" ]
        then
                pushd $SrcPath
                prefix_gcc=${GCC//gcc/ }
                #echo $prefix_gcc

      make ARCH=ARM CROSS_COMPILE=$prefix_gcc defconfig     
                make ARCH=ARM CROSS_COMPILE=$prefix_gcc -s       
                cp -r busybox  $myOBJPATH
                make distclean     
                popd
        fi

        if [ $ARCH = "android" ]
        then
      myARMCROSS=arm-linux-gnueabihf
                pushd $SrcPath

                make ARCH=ARM CC="${myARMCROSS}-gcc --static" defconfig     
                make ARCH=ARM CC="${myARMCROSS}-gcc --static" -s      
                cp -r busybox $myOBJPATH
                make distclean     
                popd
        fi
}

build_busybox
