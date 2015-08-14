build_openssl() {
    set -e
        SrcPath=$BENCH_PATH"403.openssl"
   myOBJPATH=${INSTALL_DIR}/bin
        BuildPATH="$CALIPER_TMP/build.openssl"
        TOP_SRCDIR="$CURRENT_PATH/$SrcPath"
   mkdir -p $BuildPATH

        if [ $ARCH = "x86_64" -o $ARCH = "x86_32" ]; then
            cp -rf $TOP_SRCDIR/* $BuildPATH
            pushd $BuildPATH
            if [ $ARCH = "x86_64" ]; then
                OS_OPTION="linux-x86_64"
            else
                OS_OPTION="linux"
            fi
            CC=$GCC $TOP_SRCDIR/Configure $OS_OPTION      #linux-x86_64
            make -s    
            cp apps/openssl $myOBJPATH/
            popd
            rm -rf $BuildPATH/
        fi
        if [ $ARCH = "arm_32" -o $ARCH = 'arm_64' ]; then  #-o $ARCH = "arm_64"
            cp -rf $TOP_SRCDIR/* $BuildPATH/
            pushd $BuildPATH
            if [ $ARCH = "arm_32" ] ; then
                CC=$GCC ./Configure linux-armv4    
            else
                CC=$GCC ./Configure linux-aarch64    
            fi
            make -s    
            cp apps/openssl $myOBJPATH/
            popd
            rm -rf $BuildPATH/
        fi
        if [ $ARCH = "android" ]; then
        #pushd $SrcPath
            cp -rf $TOP_SRCDIR/* $BuildPATH/
            pushd $BuildPATH
            export ANDROID_DEV=$ANDROIDSYSROOT/usr
            CC="$ANDROIDGCC --sysroot=$ANDROIDSYSROOT" 
            ./Configure android-armv7    
            make -s    
            cp apps/openssl $myOBJPATH/
            popd
            rm -rf $BuildPATH/
        #popd
        fi
}

build_openssl
