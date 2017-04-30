#!/bin/bash

if [ ! -d /usr/local/nginx ]; then 
	mkdir -p /usr/local/nginx 
	cp -r ../nginx_config_files/* /usr/local/nginx/  
fi

iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X
iptables -t mangle -F
iptables -t mangle -X
