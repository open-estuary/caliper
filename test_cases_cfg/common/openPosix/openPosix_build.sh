build_openPosix()
{
    set -e
   SrcPath=${BENCH_PATH}"302.OpenPosixTestsuite"
    if [ $ARCH = "x86_64" -o $ARCH = "x86_32" ]
   then
      cp $SrcPath ${OBJPATH}/OpenPosixTestsuite -rf
   fi
}

build_openPosix
