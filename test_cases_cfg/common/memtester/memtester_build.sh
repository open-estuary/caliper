build_memtester()
{
    set -e
    set -x

        SrcPath=${BENCH_PATH}"415.memtester"
   myOBJPATH=${INSTALL_DIR}/bin
   mkdir -p $myOBJPATH
        if [ $ARCH = "x86_64" -o $ARCH = "x86_32" ]
            then
                    pushd $SrcPath
                    make -s     
                    cp -r memtester $myOBJPATH
            make clean     
                    popd
        fi

        if [ $ARCH = "arm_64" -o $ARCH = "arm_32" ]
        then
                pushd $SrcPath
      #make CC=$GCC
                
            if [ "$(cat conf-cc | grep 'gcc')"x != ""x ]
            then
                sed -i "s/gcc/$GCC/g" conf-cc
                sed -i "s/gcc/$GCC/g" conf-ld
            else
                sed -i "s/cc/$GCC/g" conf-cc
                sed -i "s/cc/$GCC/g" conf-ld
            fi
                make      
                cp -r memtester $myOBJPATH
                make clean     
                sed -i "s/$GCC/gcc/g" conf-cc
                sed -i "s/$GCC/gcc/g" conf-ld
                popd
        fi

        if [ $ARCH = "android" ]
        then
      myARMCROSS=arm-linux-gnueabihf
                pushd $SrcPath
                make CC="${myARMCROSS}-gcc --static"    
                cp -r  memtester $myOBJPATH
                make clean     
                popd
        fi
}

build_memtester
