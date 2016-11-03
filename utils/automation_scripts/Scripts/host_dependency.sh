#!/bin/bash
host_packages=('libc6' 'libncurses5' 'libstdc++6' 'lib32z1' 'python-dev' 'nfs-common' 'build-essential' 'python-pip' 'automake' 'autoconf' 'make' 'openssh-server' 'libnuma-dev' 'texinfo' 'python-matplotlib' 'python-numpy' 'nfs-kernel-server' 'openjdk-7-jre' 'openjdk-7-jdk')
NFS_mount="/opt/caliper_nfs/ltp_log"
toolchain="/home/sana/toolchain"
ERROR="ERROR-IN-AUTOMATION"
UPDATE=0
clear 
echo "HOST"

echo "HOST DEPENDENCY"
for i in `seq 0 $((${#host_packages[@]}-1)) `
do
	#chcking to see if all the host dependent packages are installed
    check=`dpkg-query -W -f='${Status}' ${host_packages[$i]} | grep -c "ok installed"`
    if [ $check -eq 0 ] 
    then
	# if force option is passed thn forcefully run the scripts
       if [ $1 = "y" ]
       then
            choice="y"
       else
           echo "${host_packages[$i]} is not installed, would you like to install(y/n)"
           read choice
       fi

       if [ $choice = 'y'  ]
       then
            sudo dpkg --configure -a
            if [ $UPDATE = 0 ]
            then
                UPDATE=1
                sudo apt-get update &
                wait
            fi
            sudo apt-get -f build-dep ${host_packages[$i]} -y &
            wait
            sudo apt-get -f install ${host_packages[$i]} -y &
            wait
            if [ $? -ne 0 ]
            then
                echo -e "\n\t\t$ERROR:${host_packages[$i]} is not installed properly"
                exit 1
            fi
       else
           echo -e "\n\t\t$ERROR:Please install ${host_packages[$i]} and try again"
       fi
    else
       echo "${host_packages[$i]} is installed"
    fi
done

#NFS mount requirements
if [ ! -d $NFS_mount ]
then
	sudo mkdir -p $NFS_mount 
	if [ $? -ne 0 ]
	then
		echo "$ERROR:NFS MOUNTING FAILED"
		exit 1
	fi
fi
sudo chmod -R 775 /opt/caliper_nfs
if [ $? -ne 0 ]
then
	echo "$ERROR:NFS PERMISSION SETTING FAILED"
	exit 1
fi
sudo chown -R $USER:$USER /opt/caliper_nfs
if [ $? -ne 0 ]
then
	echo "$ERROR:NFS OWNER SETTING FAILED"
	exit 1
fi

#exporting the path for NFS mounting
flag=0
#command="/opt/caliper_nfs *(rw,sync,no_root_squash)"
command="/opt/caliper_nfs *(rw,sync,no_root_squash,subtree_check)"
pattern=`echo "$command" | awk -F ' ' '{ print $1 }'`
if [ `cat /etc/exports | grep -c "$pattern"` -ge 1 ]
then
    pattern=`echo "$command" | awk -F ' ' '{print $2}'`
    if [ `cat /etc/exports | grep -c "$pattern"` -ge 1 ]
    then
        flag=1
    fi
fi

if [ $flag -eq 1 ]
then
    echo "The path for NFS point is exported properly"
else
    echo "NFS mount path is not Exported"
    echo "Would u like me to do it (y/n)"
    read choice
    if [ $choice == 'y'  ]
    then
        `sudo echo "$command" >> /etc/exports`
        if [ $? -ne 0 ]
        then
            echo -e "\n\t\t$ERROR:EXPORTING THE PATH FAILED"
            exit 1
        fi
    else
       echo -e "\n\t\tPlease export the path in /etc/export and try again"
    fi
fi

#Restaring the nfs-kernal-service
echo "Restarting nfs-kernel-server"
sudo service nfs-kernel-server restart
if [ $? -ne 0 ]
then
	echo -e "\n\t\t$ERROR:RESTARTING THE NFS_KERNEL Failed"
	exit 1
fi

