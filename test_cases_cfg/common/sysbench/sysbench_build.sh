build_sysbench() {
    set -e
       SrcPath=$BENCH_PATH"315.sysbench"
   INSTALL_DIR="$INSTALL_DIR/sysbench"
   mkdir -p $INSTALL_DIR

   cp $SrcPath/*  $INSTALL_DIR 
}

build_sysbench

