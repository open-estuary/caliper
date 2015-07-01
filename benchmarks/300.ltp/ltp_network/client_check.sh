#!/bin/sh 
echo "**********The check only for suse11 platform***********"
echo "-----Start to check installation of network service in Client-----" 
set -e
check_commands="dpkg --list"
chkconfig_commands="sysv-rc-conf --list"

ret=0;
$check_commands | grep rsh-client >/dev/null || { ret=1;echo "Please install rsh-client";}
$check_commands | grep rsh-server >/dev/null || { ret=1;echo "Please install rsh-server";}
$check_commands | grep rdist >/dev/null || { ret=1;echo "Please install rdist";}
$check_commands | grep fingerd >/dev/null || { ret=1;echo "Please install finger-server";}
$check_commands | grep telnetd >/dev/null || { ret=1;echo "Please install telnet-server";}
$check_commands | grep expect >/dev/null || { ret=1;echo "Please install expect";}
#$check_commands | grep ipsec-tools >/dev/null || { ret=1;echo "Please install ipsec-tools";}
$chkconfig_commands | grep ssh >/dev/null || { ret=1;echo "Please install ssh server";}
#$chkconfig_commands | grep named >/dev/null || { ret=1;echo "Please install dns server";}

$chkconfig_commands | grep isc-dhcp >/dev/null || { ret=1;echo "Please install dhcp server";}

#$chkconfig_commands | grep ftpd >/dev/null || { ret=1;echo "Please install vsftp server";}

#$chkconfig_commands | grep apache2 >/dev/null || { ret=1;echo "Please install http server";}

if [ $ret -eq 0 ];then
    echo "Congratulations that you have installed all necessary servers."
        echo "And you can execute configureClient.sh to configure service environment."
    else
        echo "Please install and check servers again"
        exit 1
fi

exit 0
