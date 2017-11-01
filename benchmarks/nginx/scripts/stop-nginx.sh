
#!/bin/sh

TOPDIR=`pwd`

source scripts/profile

$NGINX_PATH/sbin/nginx -s stop
