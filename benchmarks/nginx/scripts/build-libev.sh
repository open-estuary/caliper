#!/bin/sh

TOPDIR=`pwd`

LIBEV=libev.tar.gz
LIBEV_DIR=libev
LIBEV_URL=https://github.com/enki/libev.git

LIBEV_PATH=$TOPDIR/install

libev_is_install()
{
	test -f $TOPDIR/install/lib/libev.so.4
}

if libev_is_install; then
	echo "$LIBEV already installed"
	#exit 0
fi

mkdir -p build

if [ ! -d build/$LIBEV_DIR ]; then
	if [ ! -f pkg/$LIBEV ]; then
		git clone $LIBEV_URL build/$LIBEV_DIR
	else
		tar xf pkg/$LIBEV -C build
	fi
fi

pushd build/$LIBEV_DIR
./configure --prefix=$LIBEV_PATH
make && make install
popd

if libev_is_install; then
	echo "export LIBEV_PATH=$LIBEV_PATH" >> scripts/profile
	echo 'export LD_LIBRARY_PATH=$LIBEV_PATH/lib:$LD_LIBRARY_PATH' >> scripts/profile
	echo 'export LD_RUN_PATH=$LIBEV_PATH/lib:$LD_RUN_PATH' >> scripts/profile
	#echo 'export PKG_CONFIG_PATH=$LIBEV_PATH/'
	echo "$LIBEV successfully install"
else
	echo "Failed to install $LIBEV"
fi
