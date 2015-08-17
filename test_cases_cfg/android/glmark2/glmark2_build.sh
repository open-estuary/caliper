build_glmark2() {
    set -e
   SrcPath=${BENCH_PATH}"442.glmark2"
   myOBJPATH=${INSTALL_DIR}/bin

   if [ $ARCH = "android" ]
   then
      #pushd $SrcPath
      #cd android
      #ndk-build
      #android   update project -p . -s -t 1
      #ant  debug
      #popd

      cp ${BENCH_PATH}/android/Glmark2-debug.apk $myOBJPATH
   fi
}

build_glmark2
