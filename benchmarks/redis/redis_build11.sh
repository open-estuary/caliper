build_redis()
{
    set -e

    SrcPath=${BENCH_PATH}"510.redis/src/"
    SrcPathbench=${BENCH_PATH}"510.redis"
    myOBJPATH=${INSTALL_DIR}/bin

    pushd $SrcPath

    if [ $ARCH = "x86_64" ]; then
	make all
	cp redis-server redis-cli $myOBJPATH
    fi

    if [ $ARCH = "arm_64" ]; then
	make distclean
	make CC=aarch64-linux-gnu-gcc all
	cp redis-server redis-cli $myOBJPATH
    fi

    popd

    pushd $SrcPathbench
    cp -r redis-config ${INSTALL_DIR}
    cp -r redis-scripts ${INSTALL_DIR}
    popd
}
   
build_redis

