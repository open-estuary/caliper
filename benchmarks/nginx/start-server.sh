#!/bin/sh

TOPDIR=${0%/*}
cd $TOPDIR

#sh scripts/start-nginx-lb.sh
#sh scripts/start-nginx-proxy.sh
scripts/start-nginx-webserver.sh
