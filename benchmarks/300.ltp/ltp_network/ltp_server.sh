#!/bin/bash 

detect_inet(){
    IFNUMS=`netstat -i | wc -l`
    IFNUMS=$(( $IFNUMS - 2 ))
    IFNAME=${IFNAME:-$(netstat -i | awk '{print $1}' | tail -n ${IFNUMS})}

    for i in ${IFNAME};do
        if ethtool ${i} | grep "Link detected: yes" > /dev/null;then
            echo "interface ${i} is available"
        fi
    done
}

rsh_config(){
    #root access rsh server without password

    FILES="rsh rlogin rexec"
    for i in ${FILES};do 
        if [ ! -e /etc/xinetd.d/${i} ]; then
            cp ./ltp/${i} /etc/xinetd.d
        fi
        pushd /etc/xinetd.d
        if [ -e ${i} -a -f ${i} ];then
            sed -i '/disable/s/yes/no/' ${i}
        fi
        popd
    done

    echo "rsh" >> /etc/securetty
    echo "rlogin" >> /etc/securetty
    echo "rexec" >> /etc/securetty

    FILE="/root/.rhosts"
    if [ ! -e $FILE ];then
        touch $FILE
    fi
    echo "$SERVER root" >> $FILE
    echo "$CLIENT root" >> $FILE

    FILE1="/etc/hosts.equiv"
    if [ -e $FILE1 ];then
        mv $FILE1 $FILE1.backup
    fi
    cp $FILE $FILE1

    pushd /etc/pam.d
    for i in ${FILES};do
        if [ -e ${i} -a -f ${i} ];then
            sed -i '/pam_securetty\.so/d' ${i}
        fi
    done
    popd
}

telnet_config()
{
    #access telnet server without password
    echo "pts/0" >> /etc/securetty
    echo "pts/1" >> /etc/securetty
    echo "pts/2" >> /etc/securetty
    echo "pts/3" >> /etc/securetty
    echo "pts/4" >> /etc/securetty
    echo "pts/5" >> /etc/securetty
    echo "pts/6" >> /etc/securetty
    echo "pts/7" >> /etc/securetty

    pushd /etc/pam.d
    if [ -e login ];then
        sed -i '/pam_securetty\.so/d' "login"
    fi
    popd
}

main()
{
    echo "*****Start to configure network service of Server Machine*****"
    chkconfig_commands="sysv-rc-conf "

    SERVER_IP=$1
    CLIENT_IP=$2
    SERVER=$(cat /etc/hostname)
    CLIENT="ltp-client"
    echo "127.0.0.1     $SERVER" >> /etc/hosts
    echo "$SERVER_IP    $SERVER" >> /etc/hosts
    echo "$CLIENT_IP    $CLIENT" >> /etc/hosts

    rsh_config
    telnet_config

    export PATH=$PATH:$PWD/ltp/testcases/bin

    #enable broadcast ping
    echo "0" > /proc/sys/net/ipv4/icmp_echo_ignore_broadcasts

    #configure share of nfs system for client
    echo "/tmp $CLIENT_IP/255.255.0.0(rw,no_root_squash,no_subtree_check,sync)" >> /etc/exports

    $chkconfig_commands rsh on
    $chkconfig_commands rlogin on
    $chkconfig_commands nfs on
    $chkconfig_commands echo on
    $chkconfig_commands echo-udp on
    $chkconfig_commands finger on
    $chkconfig_commands pure-ftpd on
    $chkconfig_commands telnet on
    $chkconfig_commands ssh on
    $chkconfig_commands named on
    service xinetd restart
    service nfs-kernel-server restart
    
    if [ ! -f tmp.log ]; then
        touch tmp.log
    fi
    nc -l 1234 > tmp.log
    cat tmp.log
    content=$(cat tmp.log)
    if [ "$content"x != ""x ]; then 
        rm -fr tmp.log
    else
        exit 1
    fi

    echo $SERVER > tmp.log
    sleep 20
    nc $CLIENT_IP 1234 < tmp.log

    eth_addr=$(ifconfig -a | grep eth[0-9] | awk '{print $1}')
    read -a eths <<< $eth_addr
    for i in ${eths[@]}
    do
        ip=$(ifconfig $i | grep 'inet addr' | awk '{print $2}' | awk -F ':' '{print $2}')
        if [ "$ip"x = "$SERVER_IP"x ]; then
            LOCAL=$(ifconfig $i | grep eth[0-9] | awk '{print $5}')
            echo $LOCAL
            break
        fi
    done
    
    echo $LOCAL > tmp.log
    sleep 30
    nc $CLIENT_IP 1234 < tmp.log
    rm -fr tmp.log

}

main $1 $2
