build_ethtool() {
    set -e
        SrcPath=${BENCH_PATH}"422.ethtool"
        BuildPATH="$CALIPER_TMP/build.ethtool"
        TOP_SRCDIR="$MYPWD/$SrcPath"
        myOBJPATH=${INSTALL_DIR}/bin

        if [ $ARCH = "arm_64" -o $ARCH = "arm_32" ]
        then
           mkdir -p $BuildPATH
                pushd $BuildPATH
                $TOP_SRCDIR/configure --host=$ARMCROSS
                make     
      $STRIP ethtool
                cp ethtool $myOBJPATH
                popd
                rm -rf $BuildPATH
        fi
}

build_ethtool

