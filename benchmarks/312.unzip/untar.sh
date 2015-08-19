#!/bin/bash
if [ -d kernel-dev ];then
    rm -fr kernel-dev
fi

if [ -f kernel-dev.tar.gz ]; then
    time tar xvzf kernel-dev.tar.gz
    if [ $? -ne 0 ]; then
        echo "There is error with the unzip process"
        return 
    fi
fi
