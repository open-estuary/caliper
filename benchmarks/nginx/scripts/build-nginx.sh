#!/bin/bash

TOPDIR=`pwd`

NGINX=nginx-1.11.4.tar.gz
NGINX_DIR=${NGINX%\.*}
NGINX_DIR=${NGINX_DIR%\.*}
NGINX_URL=http://nginx.org/download/nginx-1.11.4.tar.gz
NGINX_PATH=$TOPDIR/install

nginx_is_install()
{
	test -f $NGINX_PATH/sbin/nginx
}

#if nginx_is_install; then
#	echo "$NGINX is already installed"
#	exit 0
#fi

mkdir -p build
mkdir -p install

if [ ! -d $TOPDIR/build/$NGINX_DIR ]; then
	if [ ! -f pkg/$NGINX ]; then
		wget $NGINX_URL -O pkg/$NGINX
	fi
	tar xf pkg/$NGINX -C build
fi

if $(which apt >/dev/null 2>&1); then
	apt-get install -y build-essential
	apt-get install -y libpcre++-dev
	apt-get install -y libssl-dev
fi

pushd build/$NGINX_DIR
cd  $TOPDIR/build/$NGINX_DIR
./configure  --with-http_ssl_module --prefix=$TOPDIR/install
make && make install
popd

cp /dev/null $TOPDIR/scripts/profile

if nginx_is_install; then
	if [ ! $(grep -q "NGINX_PATH" $TOPDIR/scripts/profile) ]; then
		echo "export NGINX_PATH=$NGINX_PATH" >> $TOPDIR/scripts/profile
		echo 'export PATH=$PATH:$NGINX_PATH/sbin' >> $TOPDIR/scripts/profile
	fi

	ulimit -n 102400

	echo "$NGINX install successfully"
	exit 0
else
	echo "Failed to install $NGINX"
	exit 1
fi
