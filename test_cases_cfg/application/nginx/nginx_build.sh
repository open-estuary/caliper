build_nginx() {

        set -e
        SrcPath=${BENCH_PATH}"509.nginx"
        BuildPATH="$CALIPER_TMP/build.nginx"
        TOP_SRCDIR="$CURRENT_PATH/$SrcPath"
        myOBJPATH=${INSTALL_DIR}/bin
        mkdir -p $BuildPATH

        if [ $ARCH = "x86_64" ]
        then
                pushd $SrcPath
                ./configure
                make
                cp objs/nginx $myOBJPATH
                cp -r nginx_config_files $INSTALL_DIR
                popd

        fi

        if [ $ARCH = "arm_64" ]
        then
                pushd $SrcPath
                echo "executing cconfigure on arrm 64"
                ./configure --with-cc=aarch64-linux-gnu-gcc --with-pcre=$SrcPath/nginx-dep/pcre-8.39 --with-zlib=$SrcPath/nginx-dep/zlib-1.2.8 --with-openssl=$SrcPath/nginx-dep/openssl --with-cpp=aarch64-linux-gnu-g++
                echo "executing cconfigure on arrm 64"
                cp Makefile_arm64 objs/Makefile
                echo "c-source"
                cp ngx_auto_config.h objs/
                make
                cp objs/nginx $myOBJPATH
                cp -r nginx_config_files $INSTALL_DIR
                popd
        fi
}

build_nginx

