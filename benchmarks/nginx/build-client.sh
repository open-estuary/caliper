#!/bin/sh

TOPDIR=${0%/*}
cd $TOPDIR

scripts/build-libev.sh
scripts/build-httpress.sh
