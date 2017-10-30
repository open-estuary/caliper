#!/bin/sh

TOPDIR=${0%/*}
cd $TOPDIR

sh scripts/build-libev.sh
sh scripts/build-httpress.sh
