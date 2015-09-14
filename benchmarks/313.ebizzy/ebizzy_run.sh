#!/bin/bash

if [ ! -d ./ltp ]; then
    echo "There is not ebizzy binary"
    return
fi

pushd ./ltp/testcases/bin

for i in 1 2 4 8 16 32 64 80;do
    echo "log: ./ebizzy -t $i -S 30 -M"
    ./ebizzy -t $i -S 30 -M
done

for i in 1 2 4 8 16 32 64 80;
do
    echo "log: ./ebizzy -t $i -S 30 -m"
    ./ebizzy -t $i -S 30 -m
done
popd
