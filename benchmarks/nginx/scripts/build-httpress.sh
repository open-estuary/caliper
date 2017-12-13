#!/bin/bash

TOPDIR=`pwd`

source scripts/profile

HTTPRESS=f27fa1949044.zip
HTTPRESS_DIR=yarosla-httpress-f27fa1949044
HTTPRESS_URL=https://bitbucket.org/yarosla/httpress/get/f27fa1949044.zip
HTTPRESS_PATH=$TOPDIR/install/bin

httpress_is_install()
{
	test -f $HTTPRESS_PATH/httpress
}

if httpress_is_install; then
	echo "httpress already installed"
	exit 0
fi

if $(which apt >/dev/null 2>&1); then
	apt install -y unzip
	apt install -y libgnutls-dev
fi

if $(which yum >/dev/null 2>&1); then
	yum install -y gnutls-devel
fi

mkdir -p pkg

if [ ! -f pkg/$HTTPRESS ]; then
	wget $HTTPRESS_URL -O pkg/$HTTPRESS
fi

if [ ! -d build/$HTTPRESS_DIR ]; then
	unzip pkg/$HTTPRESS -d build
fi

mkdir -p $HTTPRESS_PATH

pushd build/$HTTPRESS_DIR
sed -i "s;\(^CFLAGS_RELEASE.*\);\1 -I$LIBEV_PATH/include;" Makefile
sed -i "s;\(^LIBS.*\);\1 -L$LIBEV_PATH/lib;" Makefile
make
cp bin/Release/httpress $HTTPRESS_PATH
popd

if httpress_is_install; then
	echo "export HTTPRESS_PATH=$HTTPRESS_PATH" >> scripts/profile
	echo 'export PATH=$HTTPRESS_PATH:$PATH' >> scripts/profile
	echo "httpress sucessfully install"
	exit 0
else
	echo "Failed to install httpress"
	exit 1
fi
