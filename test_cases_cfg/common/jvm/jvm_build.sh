build_jvm() {
    set -e
   SrcPath=${BENCH_PATH}"444.jvm"
   myOBJPATH="${INSTALL_DIR}/jvm"
   mkdir -p $myOBJPATH

    if [ $ARCH = "x86_64" -o $ARCH = "x86_32" ]
   then
      pushd $SrcPath/JavaGrandeForum
      ./build.sh     
      mv jgf_section1.jar       $myOBJPATH/
      mv jgf_section2.jar       $myOBJPATH/
      mv jgf_section3.jar       $myOBJPATH/
      cp -r section3/tunnel.dat    $myOBJPATH/
      mkdir -p                  $myOBJPATH/Data
      cp -r section3/Data/hitData           $myOBJPATH/Data/ 
      popd

      pushd $SrcPath/LinkpackJava
      ./build.sh     
      mv Linpack.jar           $myOBJPATH/
      popd

      pushd $SrcPath/scimark2
      ./build.sh   
      mv scimark2.jar          $myOBJPATH/
      popd

      pushd $SrcPath/GCBench
      ./build.sh     
      mv GCBench.jar           $myOBJPATH/
      popd
   fi

        if [ $ARCH = "arm_64" -o $ARCH = "arm_32" ]
        then
                pushd $SrcPath/JavaGrandeForum
                ./build.sh     
                mv jgf_section1.jar       $myOBJPATH
                mv jgf_section2.jar       $myOBJPATH
                mv jgf_section3.jar       $myOBJPATH
                cp section3/tunnel.dat    $myOBJPATH
                mkdir -p                  $myOBJPATH/Data
                cp section3/Data/hitData           $myOBJPATH/Data
                popd

                pushd $SrcPath/LinkpackJava
                ./build.sh     
                mv Linpack.jar           $myOBJPATH
                popd

                pushd $SrcPath/scimark2
                ./build.sh     
                mv scimark2.jar          $myOBJPATH
                popd

      pushd $SrcPath/GCBench
      ./build.sh     
      mv GCBench.jar           $myOBJPATH
      popd
        fi

        if [ $ARCH = "android" ]
        then
                pushd $SrcPath/JavaGrandeForum
                ./build.sh     
      dx --dex   --output=jgf_section1.dex jgf_section1.jar
      dx --dex   --output=jgf_section2.dex jgf_section2.jar
      dx --dex   --output=jgf_section3.dex jgf_section3.jar
      rm -rf jgf_section1.jar jgf_section2.jar jgf_section3.jar
                mv jgf_section1.dex       $myOBJPATH
                mv jgf_section2.dex       $myOBJPATH
                mv jgf_section3.dex       $myOBJPATH
                cp section3/tunnel.dat    $myOBJPATH
                mkdir -p                  $myOBJPATH/Data
                cp section3/Data/hitData           $myOBJPATH/Data
                popd

                pushd $SrcPath/LinkpackJava
                ./build.sh     
      dx --dex   --output=Linpack.dex Linpack.jar
      rm -rf Linpack.jar
                mv Linpack.dex           $myOBJPATH
                popd

                pushd $SrcPath/scimark2
                ./build.sh     
      dx --dex   --output=scimark2.dex scimark2.jar
      rm -rf scimark2.jar
                mv scimark2.dex          $myOBJPATH
                popd

      pushd $SrcPath/GCBench
      ./build.sh     
      dx --dex   --output=GCBench.dex GCBench.jar
      mv GCBench.dex           $myOBJPATH
      popd
        fi
}

build_jvm
