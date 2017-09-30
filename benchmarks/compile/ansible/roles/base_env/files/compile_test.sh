#!/bin/bash
set -x

echo $(pwd)
if [ ! -d kernel-dev ]; then
    if [ ! -f kernel-dev.tar.gz ]; then
        echo "there is no kernel-dev.tar.gz"
        return
    fi
    tar xvzf kernel-dev.tar.gz
fi

if [ $? -eq 0 ]; then
    info=$(pwd)
    arch_x86_64=$(echo $info | grep 'x86_64')
    arch_arm64=$(echo $info | grep 'aarch64')
    GCC=0
    if [ "$arch_x86_64" != "" ]; then
        GCC=aarch64-linux-gnu-gcc
    else
        GCC=gcc
    fi
    #if [ "$arch_arm64" != "" ];then
    #    GCC=gcc
    #fi
    judge_toolchain=$(which $GCC)
    if [ "$judge_toolchain" != "" ];then
        cd $(pwd)/kernel-dev
        make clean
        if [ "$GCC" = "aarch64-linux-gnu-gcc" ]; then
            export ARCH=arm64
            export CROSS_COMPILE=aarch64-linux-gnu-
            make defconfig
            time make -j$1
        else
            if [ "$GCC" = "gcc" ];then
                make defconfig 
                time make -j$1
            fi
        fi
    fi
fi
