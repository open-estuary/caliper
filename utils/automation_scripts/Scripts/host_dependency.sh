#!/bin/bash

host_dependency="host_dependency_dir"

if [ ! -d $host_dependency ]
then
	sudo mkdir -p $host_dependency
fi
cd $host_dependency

file_present=host_dependency_output_summary.txt
if [ -f $file_present ]
then
    sudo rm host_dependency_output_summary.txt
fi

host_packages=('libc6' 'libncurses5' 'libstdc++6' 'lib32z1' 'python-dev' 'nfs-common' 'build-essential' 'python-pip' 'automake' 'autoconf' 'make' 'openssh-server' 'libnuma-dev' 'texinfo' 'python-matplotlib' 'python-numpy' 'nfs-kernel-server' 'openjdk-7-jre' 'openjdk-7-jdk' 'lib32stdc++6' 'bzr' 'gfortran')

NFS_mount="/mnt/caliper_nfs/ltp_log"
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
                sudo apt-get update
            fi
            sudo apt-get -f build-dep ${host_packages[$i]} -y
            sudo apt-get -f install ${host_packages[$i]} -y
            if [ $? -ne 0 ]
            then
                echo -e "\n\t\t$ERROR:${host_packages[$i]} is not installed properly" >> host_dependency_output_summary.txt
                continue
	    else
       		echo "${host_packages[$i]} is installed" >> host_dependency_output_summary.txt
            fi
       else
           echo -e "\n\t\t$ERROR:Please install ${host_packages[$i]} and try again" >> host_dependency_output_summary.txt
       fi
    else
       echo "${host_packages[$i]} is installed" >> host_dependency_output_summary.txt
    fi
done

host_pip_packages=('Django' 'numpy' 'matplotlib' 'openpyxl')

for i in `seq 0 $((${#host_pip_packages[@]}-1)) `
do
    #chcking to see if python packages are installed
    check=`pip show ${host_pip_packages[$i]} | grep -c "${host_pip_packages[$i]}"`
    if [ $check -eq 0 ] 
    then
       # if force option is passed thn forcefully run the scripts
       if [ $1 = "y" ]
       then
            choice="y"
       else
           echo "${host_pip_packages[$i]} is not installed, would you like to install(y/n)"
           read choice
       fi

       if [ $choice = 'y'  ]
       then
            if [ ${host_pip_packages[$i]} == "Django" ]
            then
                sudo pip install Django==1.8.4
            elif [ ${host_pip_packages[$i]} == "matplotlib" ]
            then
                sudo pip install matplotlib==1.3.1
            elif [ ${host_pip_packages[$i]} == "numpy" ]
            then
                sudo pip install numpy==1.8.2
            else
                sudo pip install ${host_pip_packages[$i]}
            fi 
            if [ $? -ne 0 ]
            then
                echo -e "\n\t\t$ERROR:${host_pip_packages[$i]} is not installed properly" >> host_dependency_output_summary.txt
                continue
     	    else
       		echo "${host_pip_packages[$i]} is installed" >> host_dependency_output_summary.txt
            fi
        else
           echo -e "\n\t\t$ERROR:Please install ${host_pip_packages[$i]} and try again" >> host_dependency_output_summary.txt
        fi
     else
       echo "${host_pip_packages[$i]} is installed" >> host_dependency_output_summary.txt
     fi
done

check=`sudo find /usr/local/lib -name libpcre.so | grep -c libpcre.so`
if [ $check -ne 1 ];then
    wget http://www.estuarydev.org/caliper/pcre-8.39.tar.gz
    tar -zxvf pcre-8.39.tar.gz
    cd pcre-8.39
    ./configure
    make -j32
    sudo make install
fi

#NFS mount requirements
if [ ! -d $NFS_mount ]
then
	sudo mkdir -p $NFS_mount 
	if [ $? -ne 0 ]
	then
		echo "$ERROR:NFS MOUNTING FAILED" >> host_dependency_output_summary.txt
	fi
fi
sudo chmod -R 775 /mnt/caliper_nfs/ltp_log
if [ $? -ne 0 ]
then
	echo "$ERROR:NFS PERMISSION SETTING FAILED" >> host_dependency_output_summary.txt
fi
sudo chown -R $USER:$USER /mnt/caliper_nfs/ltp_log
if [ $? -ne 0 ]
then
	echo "$ERROR:NFS OWNER SETTING FAILED" >> host_dependency_output_summary.txt
fi

#exporting the path for NFS mounting
flag=0
#command="/opt/caliper_nfs *(rw,sync,no_root_squash)"
command="/mnt/caliper_nfs/ltp_log *(rw,sync,no_root_squash)"
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
    if [ $1 = "y" ]
    then
         choice="y"
    else
        echo "${host_pip_packages[$i]} is not installed, would you like to install(y/n)"
        read choice
    fi
    if [ $choice == 'y'  ]
    then
        `sudo echo "$command" >> /etc/exports`
        if [ $? -ne 0 ]
        then
            echo -e "\n\t\t$ERROR:EXPORTING THE PATH FAILED" >> host_dependency_output_summary.txt
        fi
    else
       echo -e "\n\t\tPlease export the path in /etc/export and try again" >> host_dependency_output_summary.txt
    fi
fi

#Restaring the nfs-kernal-service
echo "Restarting nfs-kernel-server"
sudo service nfs-kernel-server restart
if [ $? -ne 0 ]
then
	echo -e "\n\t\t$ERROR:RESTARTING THE NFS_KERNEL Failed" >> host_dependency_output_summary.txt
fi

