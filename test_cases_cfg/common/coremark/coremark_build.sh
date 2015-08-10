build_coremark() {
   set -e

   CoreMarkPath=$BENCH_PATH"400.coremark"
   myOBJPATH=${INSTALL_DIR}/bin
   pushd $CoreMarkPath
   if [ $ARCH = "x86_64" -o $ARCH = "x86_32" ]; then
      # -O2 -msse4
      make PORT_DIR=linux64 CC=$GCC XCFLAGS=" -msse4 " compile     
      cp coremark.exe $myOBJPATH/coremark
      make PORT_DIR=linux64 CC=$GCC clean     
   fi
   if [ $ARCH = "arm_32" ]; then
      # O2 -mfloat-abi=hard -mfpu=vfpv4 -mcpu=cortex-a15
      make PORT_DIR=linux CC=$GCC XCFLAGS=" -mfloat-abi=hard -mfpu=vfpv4 -mcpu=cortex-a15 " compile     
      cp coremark.exe $myOBJPATH/coremark
      make PORT_DIR=linux64 CC=$GCC compile clean     
   fi
    if [ $ARCH = "arm_64"  ]; then
        make PORT_DIR=linux64 CC=$GCC compile       # XCFLAGS=" -mabi=lp64 " compile
        cp coremark.exe $myOBJPATH/coremark
        make PORT_DIR=linux64 CC=$GCC clean     
    fi
   if [ $ARCH = "android" ]; then
      ndk-build    
      cp  libs/armeabi-v7a/coremark $myOBJPATH/
      ndk-build clean     
      rm -rf libs/ obj/
   fi
   popd

}

build_coremark

