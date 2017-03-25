build_fio()
{
    set -e
   SrcPath=${BENCH_PATH}"432.fio"

   if [ $ARCH = "x86_64" -o $ARCH = "x86_32" ]
      then
      pushd $SrcPath
      make clean     
      ./configure     
      make -j16     
      #make install
      cp ./fio  $INSTALL_DIR/bin
      popd
   fi
    if [ $ARCH = "arm_64" -o $ARCH = "arm_32" ]
      then
      pushd $SrcPath
      make clean     
      if [ $ARCH = "arm_32" ]
      then
          ./configure --cpu=arm --cc=arm-linux-gnueabihf-gcc     
          make     
          cp ./fio $INSTALL_DIR/bin
      fi
      if [ $ARCH = "arm_64" ]
      then
          ./configure --cpu=arm --cc=aarch64-linux-gnu-gcc     
          make     
          #make install
      fi
      cp ./fio $INSTALL_DIR/bin
      popd
   fi
}

build_fio

