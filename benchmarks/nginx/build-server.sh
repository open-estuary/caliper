#!/bin/sh

TOPDIR=${0%/*}
cd $TOPDIR

sh scripts/build-nginx.sh
#sh scripts/make-ca.sh
