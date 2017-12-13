#!/bin/sh

TOPDIR=${0%/*}
cd $TOPDIR

scripts/build-nginx.sh
#sh scripts/make-ca.sh
