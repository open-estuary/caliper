#!/bin/bash
url='www.estuarydev.org/caliper'
#url='http://7xjz0v.com1.z0.glb.clouddn.com/caliper_tools'
filename='kernel-dev.tar.gz'

build_compile() {
    set -e
    set -x
    Path=$BENCH_PATH"312.unzip"
    myOBJPATH=${INSTALL_DIR}/scripts
    if [ ! -d $myOBJPATH ]; then
        mkdir -p $myOBJPATH
    fi
    download_file $download_dir $url $filename
    if [ $? -ne 0 ]; then
        echo 'Downloading dependency software (kernel-dev.tar.gz) error'
        exit 1
    fi
    if [ ! -f $myOBJPATH/$filename ]; then
        cp $download_dir/$filename $myOBJPATH
    fi
    cp $Path/* $myOBJPATH
}

build_compile

