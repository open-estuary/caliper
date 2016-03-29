#!/bin/bash
url='www.estuarydev.org/caliper'
#url='http://7xjz0v.com1.z0.glb.clouddn.com/caliper_tools'
filename='kernel-dev.tar.gz'

build_compile() {
    set -e
    Path=$BENCH_PATH"311.compile"
    myOBJPATH=${INSTALL_DIR}/scripts

    if [ ! -d $myOBJPATH ]; then
        mkdir -p $myOBJPATH
    fi

    pushd $Path
    # download the file
    download_file $download_dir $url $filename
    if [ $? -ne 0 ]; then
        echo "Downloading the $filename (namely the dependency
        software failed)"
        return
    fi
    if [ ! -f $myOBJPATH/$filename ]; then
        cp $download_dir/$filename $myOBJPATH
    fi
    cp *.sh $myOBJPATH
    popd
}

build_compile

