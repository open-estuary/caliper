url='www.estuarydev.org/caliper'
#url='http://7xjz0v.com1.z0.glb.clouddn.com/caliper_tools'
filename1='hadoop-2.6.0.tar.gz'
filename2='HiBench.tar.gz'
filename3='spark-1.5.1.tgz'

build_hibench() {
    SrcPath=$BENCH_PATH"314.hadoop"
    INSTALL_DIR="$INSTALL_DIR/hadoop"
    if [ ! -f $INSTALL_DIR ]; then
        mkdir -p $INSTALL_DIR
    fi

    HADOOP_DIR=$INSTALL_DIR/hadoop
    HIBENCH_DIR=$INSTALL_DIR/hibench
    SPARK_DIR=$INSTALL_DIR/spark

    cp $SrcPath/*.sh  $INSTALL_DIR
    ####
    download_file $download_dir $url $filename1
    if [ $? -ne 0 ]; then
        echo 'Download hadoop failed'
        exit 1
    fi

    tar xzf $download_dir/$filename1 -C $INSTALL_DIR
    mv $INSTALL_DIR/hadoop-2.6.0  $HADOOP_DIR
    ####
    download_file $download_dir $url $filename3
    if [ $? -ne 0 ]; then
        echo 'Download spark failed'
        exit 1
    fi
    tar xzf $download_dir/$filename3 -C $INSTALL_DIR
    mv $INSTALL_DIR/spark-1.5.1  $SPARK_DIR
    ####

    download_file $download_dir $url $filename2
    if [ $? -ne 0 ]; then
        echo 'Download hibench failed'
        exit 1
    fi

    tar xzf $download_dir/$filename2  -C $INSTALL_DIR
    mv $INSTALL_DIR/HiBench $HIBENCH_DIR
    ####
    rm -fr $HADOOP_DIR/etc/hadoop
    tar xzf $SrcPath/hadoop_conf.tar.gz -C $HADOOP_DIR/etc

    if [ $ARCH = "arm_64" ]; then
        rm -fr $HADOOP_DIR/lib
        tar xzf $SrcPath/hadoop_native_lib.tar.gz -C $HADOOP_DIR/
    fi
    cd $INSTALL_DIR/../
    tar cvf hadoop_tar.gz hadoop
    cd -
}

build_hibench

