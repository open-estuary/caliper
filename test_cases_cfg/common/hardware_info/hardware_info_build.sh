build_hardware() {
    set -x
    SrcPath=$BENCH_PATH"502.Hardware_info"
    INSTALL_DIR="$INSTALL_DIR/hardware_info"
    mkdir -p $INSTALL_DIR
    cp $SrcPath/* $INSTALL_DIR/
}
build_hardware
