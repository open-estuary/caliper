build_v8() {
    set -e
   SrcPath=$BENCH_PATH"440.v8"
   myOBJPATH="${INSTALL_DIR}/browser"
    BROWSER=${BENCH_PATH}/441.browser
   rm -rf   $myOBJPATH
   mkdir -p $myOBJPATH
    if [ $ARCH = "x86_64" -o $ARCH = "x86_32" ]
   then
      pushd $SrcPath
      make werror=no x64.release     
      cp  out/x64.release/d8  $myOBJPATH/
      make clean     
      popd
      cp -rf $BROWSER/v8benchmark      $myOBJPATH/
      cp -rf $BROWSER/octane-bench     $myOBJPATH/
      cp -rf $BROWSER/sunspider-bench  $myOBJPATH/
      cp -rf $BROWSER/CanvasMark       $myOBJPATH/
      cp -rf $BROWSER/webgl-bench      $myOBJPATH/
      rm -rf `find $SrcPath/build/ -name "*.pyc" -print`
      rm -rf $SrcPath/tools/jsmin.pyc
      rm -rf $SrcPath/out/* -rf
   fi

        if [ $ARCH = "android" ]
        then
                pushd $SrcPath
      make android_arm.release ANDROID_NDK_ROOT=$ANDROID_NDK_PATH ANDROID_NDK_HOST_ARCH=x86 armfpu=neon armfloatabi=softfp     
      cp out/android_arm.release/d8 $myOBJPATH/
                make clean     
                popd
                cp -rf $BROWSER/v8benchmark      $myOBJPATH/
                cp -rf $BROWSER/octane-bench     $myOBJPATH/
                cp -rf $BROWSER/sunspider-bench  $myOBJPATH/
                cp -rf $BROWSER/CanvasMark       $myOBJPATH/
                cp -rf $BROWSER/webgl-bench      $myOBJPATH/
      rm -rf `find $SrcPath/build/ -name "*.pyc" -print`
      rm -rf $SrcPath/tools/jsmin.pyc
      rm -rf $SrcPath/out/* -rf
        fi
}

build_v8
