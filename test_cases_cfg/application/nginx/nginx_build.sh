build_nginx() {

        set -e
        SrcPath=${BENCH_PATH}"509.nginx"
        myOBJPATH=${INSTALL_DIR}/nginx
        mkdir -p $myOBJPATH

        if [ $ARCH = "x86_64" ]
        then
                pushd $SrcPath
                ./configure
                make
                cp objs/nginx $myOBJPATH
                cp -r nginx_config_files $myOBJPATH
                cp -r nginx_scripts $myOBJPATH
		mv $myOBJPATH/nginx_config_files/conf/nginx_x86_64.conf $myOBJPATH/nginx_config_files/conf/my_nginx.conf
                popd
        fi

        if [ $ARCH = "arm_64" ]
        then
                pushd $SrcPath
                ./configure --with-cc=aarch64-linux-gnu-gcc --with-pcre=$SrcPath/nginx-dep/pcre-8.39 --with-zlib=$SrcPath/nginx-dep/zlib-1.2.8 --with-openssl=$SrcPath/nginx-dep/openssl --with-cpp=aarch64-linux-gnu-g++
                cp Makefile_arm64 objs/Makefile
                cp ngx_auto_config.h objs/
                make
                cp objs/nginx $myOBJPATH
                cp -r nginx_config_files $myOBJPATH
                cp -r nginx_scripts $myOBJPATH
		mv $myOBJPATH/nginx_config_files/conf/nginx_arm64.conf $myOBJPATH/nginx_config_files/conf/my_nginx.conf
                popd
        fi
	
	cd $INSTALL_DIR
	tar -cvf nginx_tar.gz nginx
	rm -fr nginx
}

build_nginx
