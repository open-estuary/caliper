#!/bin/bash

detect_inet(){
    IFNUMS=`netstat -i | wc -l`
    IFNUMS=$(( $IFNUMS - 2 ))
    IFNAME=${IFNAME:-$(netstat -i | awk '{print $1}' | tail -n ${IFNUMS})}

    for i in ${IFNAME};do
        if ethtool ${i} | grep "Link detected: yes" > /dev/null;then
            echo "interface ${i} is available"
            ETH_LIB6=${ETH_LIB6:-${i}}
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
    echo "$SERVER root" > $FILE
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

ftp_config(){
    #enable anonymous upload to ftp
    FILE="/etc/vsftpd.conf"
    if [ ! -e $FILE ];then
        echo "$FILE is not present.Please execute checkClient.sh to check service"
        exit 1
    fi
    touch ${FILE}.tmp
    cp $FILE ${FILE}.backup

    sed -i '/write_enable/s/#//' $FILE
    sed -i '/anon_other_write_enable/s/#//' $FILE 
    sed -i '/anon_other_write_enable/s/NO/YES/' $FILE
    sed -i '/anon_mkdir_write_enable/s/#//' $FILE
    sed -i '/anon_mkdir_write_enable/s/NO/YES/' $FILE
    sed -i '/anon_upload_enablei/s/#//' $FILE 
    sed -i '/anon_upload_enablei/s/NO/YES/' $FILE
    sed -i 's/listen=YES/listen_ipv6=YES/' $FILE

    sed -i 's/root/#root/'  /etc/ftpusers

    pushd /srv/ftp
    if [ -e "pub" ];then
        if [ ! -d "pub" ];then
            mv pub pub.backup
            mkdir pub
        fi
    else
        mkdir pub
    fi

    chown ftp pub
    chmod 777 pub
    popd
}

stress_config(){
    #configure for stress test 
    MAC_addr=$(ifconfig -a | grep eth[0-9] | awk '{print $1}')
    read -a MAC_array <<< $MAC_addr
    for i in ${MAC_array[@]}
    do
        ip=$(ifconfig $i | grep 'inet addr' |awk '{print $2}' | awk -F ':' '{print $2}')
        if [ "$ip"x = "$CLIENT_IP"x ]; then
            LOCAL=$(ifconfig $i | grep eth[0-9] | awk '{print $5}')
            break
        fi
    done

    nc -l 1234 > out.log
    REMOTE=$(cat out.log)
    echo "export LHOST_HWADDRS=${LOCAL}"   >> ~/.bashrc
    echo "export RHOST_HWADDRS=${REMOTE}"   >> ~/.bashrc
    echo "export NS_DURATION=3600s"   >> ~/.bashrc
    echo "export NS_TIMES=10000"   >> ~/.bashrc
    echo "export FTP_DOWNLOAD_DIR=/srv/ftp"   >> ~/.bashrc
    echo "export FTP_UPLOAD_DIR=/srv/ftp"   >> ~/.bashrc
    echo "export FTP_UPLOAD_URLDIR=pub"   >> ~/.bashrc
    echo "export HTTP_DOWNLOAD_DIR=/srv/www"   >> ~/.bashrc
    echo "export IF_UPDOWN_TIMES=10000"   >> ~/.bashrc
    echo "export MTU_CHANGE_TIMES=100"   >> ~/.bashrc
    echo "export MCASTNUM_HEAVY=40000"   >> ~/.bashrc
    echo "export IP_TOTAL_FOR_TCPIP=100"   >> ~/.bashrc
    echo "export CONNECTION_TOTAL=4000"   >> ~/.bashrc
}

main(){
    echo "*****Start to configure network service of Client Machine*****"

    chkconfig_commands="sysv-rc-conf "
    SERVER_IP=$1
    CLIENT_IP=$2

    # transfer the hostname to server

    echo "ltp-client" > /etc/hostname
    hostname ltp-client
    if [ -f out.log ]; then
        rm -fr out.log
    fi
    cp ~/.bashrc ~/.bashrc_tmp
        touch out.log
    echo "1234" > out.log
    cat out.log
    sleep 40
    nc $SERVER_IP 1234 < out.log
    sleep 2
    nc -l 1234 > out.log
    SERVER=$(cat out.log)
    
    CLIENT=$(cat /etc/hostname)
    echo "Client Name: $CLIENT IP: $CLIENT_IP"
    echo "Server Name: $SERVER IP: $SERVER_IP"
    echo "127.0.0.1     ltp-client" >> /etc/hosts
    echo "$SERVER_IP    $SERVER" >> /etc/hosts
    echo "$CLIENT_IP    ltp-client" >> /etc/hosts

    echo "export LTPROOT=$PWD/ltp"   >> ~/.bashrc
    echo "export RHOST=$SERVER"   >> ~/.bashrc
    echo "export PASSWD=123456"   >> ~/.bashrc
    echo "export PATH=$PATH:$PWD/ltp/testcases/bin:$PWD/ltp/bin"   >> ~/.bashrc

    #for ssh testcases in tcp_cmds
    echo "export TEST_USER=root"   >> ~/.bashrc
    echo "export TEST_USER_PASSWD=$PASSWD"   >> ~/.bashrc

    #enable broadcast ping
    echo "0" > /proc/sys/net/ipv4/icmp_echo_ignore_broadcasts

    rsh_config
    telnet_config
    detect_inet
    ftp_config
    stress_config

    #for lib6 testcases
    echo "Use interface $ETH_LIB6 for lib6 testcases"
    ip -6 addr add 2001:660:4701:1001::1 dev $ETH_LIB6 >/dev/null
    #sed -i "s/^/::1       $CLIENT&/g" /etc/hosts
    #sed -i "s/^/127.0.0.1 $CLIENT localhost&/g"  /etc/hosts

    #dhcpd test
    pushd /var/lib/dhcp/
    if [ ! -e "dhcpd.leases" ]; then
        touch "dhcpd.leases"
    fi
    popd

    $chkconfig_commands echo on
    $chkconfig_commands echo-udp on
    $chkconfig_commands finger on
    $chkconfig_commands telnet on
    $chkconfig_commands named on

    service xinetd restart
    service ssh restart
    service vsftpd restart
}

main $1 $2
