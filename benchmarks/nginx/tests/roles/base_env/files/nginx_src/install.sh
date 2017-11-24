build_nginx() {

    architecture_x86_64=`uname -a | grep -c "x86_64"`
    architecture_arm64=`uname -a | grep -c "aarch64"`

    ARCH=`uname -i`
    if [ $ARCH = "aarch32" ]; then
        ARMCROSS=arm-linux-gnueabihf
        GCC=${ARMCROSS}-gcc
        STRIP=${ARMCROSS}-strip
    elif [ $ARCH = "aarch64" ]; then
        ARMCROSS=aarch64-linux-gnu
        GCC=${ARMCROSS}-gcc
        STRIP=${ARMCROSS}-strip
    fi

    if [ $ARCH = "x86_64" -o $ARCH = "x86_32" ]; then
        GCC=gcc
        STRIP=strip
    fi

    set -e
    SrcPath=/tmp/nginx_src
    myOBJPATH=/tmp/nginx
    mkdir -p $myOBJPATH

    if [ $ARCH = "x86_64" ]
    then
        #./configure --with-pcre=$SrcPath/nginx-dep/pcre-8.39 --with-zlib=$SrcPath/nginx-dep/zlib-1.2.8 --with-openssl=$SrcPath/nginx-dep/openssl
        ./configure
        make
        cp objs/nginx $myOBJPATH
        cp -r nginx_config_files $myOBJPATH
        cp -r nginx_scripts $myOBJPATH
        mv $myOBJPATH/nginx_config_files/conf/nginx_x86_64.conf $myOBJPATH/nginx_config_files/conf/my_nginx.conf
    fi

    if [ $ARCH = "aarch64" -a $architecture_x86_64 -gt 0 ]
    then
        ./configure --with-cc=aarch64-linux-gnu-gcc --with-pcre=$SrcPath/nginx-dep/pcre-8.39 --with-zlib=$SrcPath/nginx-dep/zlib-1.2.8 --with-openssl=$SrcPath/nginx-dep/openssl --with-cpp=aarch64-linux-gnu-g++
        cp Makefile_arm64 objs/Makefile
        cp ngx_auto_config.h objs/
        make
        cp objs/nginx $myOBJPATH
        cp -r nginx_config_files $myOBJPATH
        cp -r nginx_scripts $myOBJPATH
        mv $myOBJPATH/nginx_config_files/conf/nginx_arm64.conf $myOBJPATH/nginx_config_files/conf/my_nginx.conf
    fi

    if [ $ARCH = "aarch64" -a $architecture_arm64 -gt 0 ]
    then
        ./configure --with-pcre=$SrcPath/nginx-dep/pcre-8.39 --with-zlib=$SrcPath/nginx-dep/zlib-1.2.8 --with-openssl=$SrcPath/nginx-dep/openssl
        make
        cp objs/nginx $myOBJPATH
        cp -r nginx_config_files $myOBJPATH
        cp -r nginx_scripts $myOBJPATH
        mv $myOBJPATH/nginx_config_files/conf/nginx_arm64.conf $myOBJPATH/nginx_config_files/conf/my_nginx.conf
    fi

    #cd /tmp
    #tar -cvf nginx_tar.gz nginx
    #rm -fr nginx
}

build_nginx
