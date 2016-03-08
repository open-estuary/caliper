build_tiny() {
   set -e

   CoreMarkPath=$BENCH_PATH"500.tinymembench"
   myOBJPATH=${INSTALL_DIR}/bin
   pushd $CoreMarkPath
   if [ $ARCH = "x86_64" -o $ARCH = "x86_32" ]; then
# -O2 -msse4
	make 
	cp tinymembench $myOBJPATH/tinymembench
	make CC=$GCC clean
   fi
   if [ $ARCH = "arm_32" ]; then
      # O2 -mfloat-abi=hard -mfpu=vfpv4 -mcpu=cortex-a15
	CC=$GCC CFLAGS="-O2 -mcpu=cortex-a9" make
	cp tinymembench  $myOBJPATH/tinymembench
	make  CC=$GCC clean
   fi
   if [ $ARCH = "arm_64"  ]; then
	CC=$GCC CFLAGS="-O2 -mcpu=cortex-a57" make       # XCFLAGS=" -mabi=lp64 " compile
	cp tinymembench $myOBJPATH/tinymembench
	make  CC=$GCC clean
   fi
   #if [ $ARCH = "android" ]; then
	#ndk-build
	#cp  libs/armeabi-v7a/coremark $myOBJPATH/
	#ndk-build clean
	#rm -rf libs/ obj/
   #fi
   popd

}

build_tiny

