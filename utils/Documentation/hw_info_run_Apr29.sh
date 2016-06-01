#!/bin/bash                                   

filename=`hostname`_"Targetinfo"
if [ -d $filename ]
then
	echo "Removing file"
	rm $filename
fi
touch `hostname`_"Targetinfo"

exec > $filename
echo
echo
echo
echo "1.cat /proc/cpuinfo"
echo
cat /proc/cpuinfo
echo
echo
echo
echo "2.cat /proc/meminfo"
echo
cat /proc/meminfo 
echo
echo
echo
echo "3.lscpu"
echo
lscpu 
echo
echo
echo
echo "4.lshw"
echo
lshw
echo
echo
echo
echo "5.fdisk -l"
echo
fdisk -l
echo
echo
echo
echo "6.df -mP"
echo
df -mP 
echo
echo
echo
echo "7.uname -a"
echo
uname -a 
echo
echo
echo
echo "8.lspci -vvnn"
echo
lspci -vvnn 
echo
echo
echo
echo "9.gcc --version"
echo
gcc --version 
echo
echo
echo
echo "10.ld --version"
echo
ld --version 
echo
echo
echo
echo "11.hostname"
echo
hostname 
echo
echo
echo
echo "12.ifconfig -a"
echo
ifconfig -a 
echo
echo
echo
echo "13.brctl show"
echo
brctl show 
echo
echo
echo
echo "14. cat /proc/cmdline"
echo
cat /proc/cmdline 
echo
echo
echo
echo "15. lsblk -o NAME,FSTYPE,MOUNTPOINT,SIZE,MODEL,PHY-SEC,SCHED,TYPE"
echo
lsblk -o NAME,FSTYPE,MOUNTPOINT,SIZE,MODEL,PHY-SEC,SCHED,TYPE,VENDOR,TRAN,REV 
echo
echo
echo
echo "16. dmesg" 
echo
dmesg 
echo
echo
echo
echo "17. cat /var/log/syslog"  
echo
cat /var/log/syslog 
echo
echo
echo
echo "18. dmidecode"
echo
dmidecode 
echo
echo
echo
echo "19. ps -ef"
echo
ps -ef 
echo
echo
echo
echo "20. lsdev"
echo
lsdev 
echo
echo
echo
echo "21. lsb_release -a"
echo
lsb_release -a 
echo
echo
echo
echo "22. mount"
echo
mount
echo
echo
echo
echo "23. cat/etc/fstab"
echo
cat /etc/fstab

echo
echo
echo
echo "24. zcat/proc/config > running.config"
echo
zcat /proc/config.gz
echo
echo
echo
echo "25.cat /proc/cmdline"
echo
cat /proc/cmdline
exec > 1
