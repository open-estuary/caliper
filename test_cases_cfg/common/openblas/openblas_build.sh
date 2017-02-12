build_OpenBLAS() {
	set -e

	SrcPath="${BENCH_PATH}506.OpenBLAS"
        myOBJPATH="${INSTALL_DIR}/bin"
        
	pushd $SrcPath
   	if [ $ARCH = "x86_64" -o $ARCH = "x86_32" ]; then
      		make 
       		pushd benchmark
        	make
         	cp sgemm.goto $myOBJPATH/
		popd
        fi

   	if [ $ARCH = "arm_64" ]; then
		make CC=aarch64-linux-gnu-gcc FC=aarch64-linux-gnu-gfortran HOSTCC=gcc TARGET=ARMV8
         	pushd benchmark
          	make CC=aarch64-linux-gnu-gcc FC=aarch64-linux-gnu-gfortran HOSTCC=gcc TARGET=ARMV8
         	cp sgemm.goto $myOBJPATH/
		popd
	fi
	popd
}

build_OpenBLAS

