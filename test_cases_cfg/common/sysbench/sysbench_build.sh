filename='sysbench-0.5'
build_sysbench() {
    set -x
    SrcPath=$BENCH_PATH"315.sysbench"
    INSTALL_DIR="$INSTALL_DIR/sysbench"
    mkdir -p $INSTALL_DIR

    if [ ! -d $download_dir/$filename ]; then
        if hash bzr; then
            bzr branch lp:~sysbench-developers/sysbench/0.5 $download_dir/$filename
            if [ $? -ne 0 ]; then
                echo 'Download sysbench-0.5 failed'
                rm -fr $download_dir/$filename
            fi
        else
            echo "bzr has not been installed"
            exit 1
        fi
    fi

    cp $SrcPath/*  $INSTALL_DIR
    cp -r $download_dir/$filename $INSTALL_DIR
    cd $INSTALL_DIR/../
    tar -cvf sysbench_tar.gz sysbench
    rm -fr sysbench
}

build_sysbench

