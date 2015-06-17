#!/bin/sh 
echo "**********The check only for suse11 platform***********"
echo "-----Start to check installation of network service in Server-----"

check_commands="dpkg --list"
chkconfig_commands="sysv-rc-conf --list"

ret=0;
$check_commands | grep rsh-server >/dev/null || { ret=1;echo "Please install rsh-server";}
$check_commands | grep rsh-client >/dev/null || { ret=1;echo "Please install rsh-client";}
$check_commands | grep rsync >/dev/null || { ret=1;echo "Please install rsync";}
$check_commands | grep telnetd >/dev/null || { ret=1;echo "Please install telnet-server";}
$check_commands | grep fingerd >/dev/null || { ret=1;echo "Please install finger-server";}
$check_commands | grep pure-ftpd >/dev/null || { ret=1;echo "Please install pure-ftpd";}
$check_commands | grep rdist >/dev/null || { ret=1;echo "Please install rdist";}
$check_commands | grep rwho >/dev/null || { ret=1;echo "Please install rwho";}
$check_commands | grep rusersd >/dev/null || { ret=1;echo "Please install rusersd";}

$check_commands | grep rstatd >/dev/null || { ret=1;echo "Please install rstatd";}
$check_commands | grep expect >/dev/null || { ret=1;echo "Please install expect";}
$chkconfig_commands | grep ssh >/dev/null || { ret=1;echo "Please install ssh server";}
#$chkconfig_commands | grep named >/dev/null || { ret=1;echo "Please install dns server";}
#$chkconfig_commands | grep ipsec-tools >/dev/null || { ret=1;echo "Please install ipsec-tools";}
$chkconfig_commands | grep nfs > /dev/null || { ret=1;echo "Please install nfsserver"; }

if [ $ret -eq 0 ];then
    echo "Congratulations that you have installed all necessary servers."
        echo "And you can execute configureServer.sh to configure service environment."
else
    echo "Please install and check servers again"
    exit 1
fi

