build_stressapptest ()
{
    set -e
        SrcPath=${BENCH_PATH}"310.stressapptest"
        BuildPATH="$CALIPER_TMP/build.stressapptest"
   TOP_SRCDIR="$CURRENT_PATH/$SrcPath"
   myOBJPATH=${INSTALL_DIR}/bin

        if [ $ARCH = "x86_64" -o $ARCH = "x86_32" ]
        then
            mkdir -p $BuildPATH
                pushd $BuildPATH
            $TOP_SRCDIR/configure     
            make     
            cp src/stressapptest $myOBJPATH
            popd
            rm -rf $BuildPATH
        fi

        if [ $ARCH = "arm_64" -o $ARCH = "arm_32" ]
        then
                mkdir -p $BuildPATH
                pushd $BuildPATH
            if [ $ARCH = "arm_32" ]; then
                $TOP_SRCDIR/configure --target=armv7a-none-linux-gnueabi --host=$ARMCROSS     
            else
                $TOP_SRCDIR/configure       #--target=armv8a-none-linux-gnueabi --host=$ARMCROSS
            fi
                make     
                cp src/stressapptest $myOBJPATH
                popd
                rm -rf $BuildPATH
        fi

        if [ $ARCH = "android" ]
        then
      pushd $SrcPath
                ndk-build     
      cp libs/armeabi/stressapptest $myOBJPATH
      ndk-build distclean
      rm -rf libs obj
      popd
        fi
}

build_stressapptest
