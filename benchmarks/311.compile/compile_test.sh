#!/bin/bash
set -x

echo $(pwd)
if [ ! -d $(pwd)/kernel-dev ]; then
    if [ ! -f $(pwd)/kernel-dev.tar.gz ]; then
        echo "there is no kernel-dev.tar.gz"
        return 
    fi
    tar xvzf $(pwd)/kernel-dev.tar.gz
fi

if [ $? -eq 0 ]; then
    info=$(pwd)
    arch_x86_64=$(echo $info | grep 'x86_64')
    arch_arm64=$(echo $info | grep 'arm_64')
    GCC=0
    if [ "$arch_x86_64"x != ""x ]; then
        GCC=aarch64-linux-gnu-gcc
    fi
    if [ "$arch_arm64"x != ""x ];then
        GCC=gcc
    fi
    judge_toolchain=$(which $GCC)
    if [ "$judge_toolchain"x != ""x ];then 
        cd $(pwd)/kernel-dev
        make clean
        if [ "$GCC"x = "aarch64-linux-gnu-gcc"x ]; then
            export ARCH=arm64
            export CROSS_COMPILE=aarch64-linux-gnu-
            make defconfig
            time make -j$1
        else
            if [ "$GCC"x = "gcc"x ];then
                make defconfig 
                time make -j$1
            fi
        fi
    fi
fi
