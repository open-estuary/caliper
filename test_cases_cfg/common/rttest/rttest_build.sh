build_rttest()
{
    set -e
       SrcPath=${BENCH_PATH}"303.RTtest"
   myOBJPATH=$INSTALL_DIR/rttest
   mkdir -p $myOBJPATH
        if [ $ARCH = "x86_64" -o $ARCH = "x86_32" ]
            then
                    pushd $SrcPath
                    make -s     
            cp -rf cyclictest    $myOBJPATH
            cp -rf hackbench     $myOBJPATH
            cp -rf pip_stress    $myOBJPATH
            cp -rf pi_stress     $myOBJPATH
            cp -rf pmqtest       $myOBJPATH
            cp -rf ptsematest    $myOBJPATH
            cp -rf rt-migrate-test     $myOBJPATH
            cp -rf sendme        $myOBJPATH
            cp -rf signaltest    $myOBJPATH
            cp -rf sigwaittest   $myOBJPATH
            cp -rf svsematest   $myOBJPATH
            make clean     
                    popd
        fi

        if [ $ARCH = "arm_64" -o $ARCH = "arm_32" ]
        then
                pushd $SrcPath
      make CC=$GCC -s     
                cp -rf cyclictest    $myOBJPATH
                cp -rf hackbench     $myOBJPATH
                cp -rf pip_stress    $myOBJPATH
                cp -rf pi_stress     $myOBJPATH
                cp -rf pmqtest       $myOBJPATH
                cp -rf ptsematest    $myOBJPATH
                cp -rf rt-migrate-test     $myOBJPATH
                cp -rf sendme        $myOBJPATH
                cp -rf signaltest    $myOBJPATH
                cp -rf sigwaittest   $myOBJPATH
                cp -rf svsematest   $myOBJPATH
                make clean     
                popd
        fi

        if [ $ARCH = "android" ]
        then
      myARMCROSS=arm-linux-gnueabihf
                pushd $SrcPath
                make CC="${myARMCROSS}-gcc --static"     
                cp -rf cyclictest    $myOBJPATH
                cp -rf hackbench     $myOBJPATH
                cp -rf pip_stress    $myOBJPATH
                cp -rf pi_stress     $myOBJPATH
                cp -rf pmqtest       $myOBJPATH
                cp -rf ptsematest    $myOBJPATH
                cp -rf rt-migrate-test     $myOBJPATH
                cp -rf sendme        $myOBJPATH
                cp -rf signaltest    $myOBJPATH
                cp -rf sigwaittest   $myOBJPATH
                cp -rf svsematest   $myOBJPATH
                make clean     
                popd
        fi
}

build_rttest
