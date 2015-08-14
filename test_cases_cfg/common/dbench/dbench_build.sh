build_dbench()
{
    set -e
       SrcPath=${BENCH_PATH}"431.dbench"
        BuildPATH="$CALIPER_TMP/build.dbench"
        TOP_SRCDIR="$CURRENT_PATH/$SrcPath"
        mkdir -p $BuildPATH
        if [ $ARCH = "x86_64" -o $ARCH = "x86_32" ]
        then
             pushd $TOP_SRCDIR
             ./autogen.sh
                $TOP_SRCDIR/configure     
                make -j 16 
                mkdir -p $INSTALL_DIR/dbench
                cp dbench    $INSTALL_DIR/dbench
                cp -r $TOP_SRCDIR/loadfiles $INSTALL_DIR/dbench
                make clean     
                popd
        fi

     if [ $ARCH = "arm_64" ]
   then
#   	  ARMCROSS=arm-linux
#      pushd $TOP_SRCDIR
#      ./autogen.sh
#      $TOP_SRCDIR/configure CC=$GCC --target=$ARMCROSS  --host=$ARMCROSS
#      LIBS="-L /opt/arm_64/lib" 
#      make      
#      cp dbench    $INSTALL_DIR/dbench
#      cp -r $TOP_SRCDIR/loadfiles $INSTALL_DIR/dbench
#        make clean     
#      popd
        exit -1
   fi
   if [ $ARCH = "arm_32" ]
   then
#   	  ARMCROSS=arm-linux
#      pushd $TOP_SRCDIR
#      ./autogen.sh
#      $TOP_SRCDIR/configure CC=$GCC --target=$ARMCROSS  --host=$ARMCROSS
#      LIBS="-L /opt/arm_32/lib"
#      #$TOP_SRCDIR/configure CC=$GCC     
#      make      
#      cp dbench    $INSTALL_DIR/dbench
#      cp -r $TOP_SRCDIR/loadfiles $INSTALL_DIR/dbench
#        make clean     
#      popd
        exit -1
   fi
        rm -rf $BuildPATH
}

build_dbench
if [ $? -eq 0 ]
then
    flag=0
else
    flag=1
fi

