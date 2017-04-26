#!/bin/bash

target_dependency="target_dependency_dir"

if [ ! -d $target_dependency ]
then
        sudo mkdir -p $target_dependency
fi
cd $target_dependency

file_present=target_dependency_output_summary.txt
if [ -f $file_present ]
then
    sudo rm target_dependency_output_summary.txt
fi

ERROR="ERROR-IN-AUTOMATION"
UPDATE=0
clear

Osname_Ubuntu=`cat /etc/*release | grep -c "Ubuntu"`
Osname_CentOS=`cat /etc/*release | grep -c "CentOS"`

architecture_x86_64=`uname -a | grep -c "x86_64"`
architecture_arm64=`uname -a | grep -c "aarch64"`

echo "TARGET"
echo -e "\n\t\t Target dependency"

if [ ! $Osname_Ubuntu -eq 0 ]
then
    if [ ! $architecture_x86_64 -eq 0 ]
    then
    	target_packages=('stress' 'make' 'build-essential' 'linux-tools-generic' 'linux-tools-common' 'gcc g++' 'nfs-common' 'automake' 'autoconf' 'autogen' 'libtool' 'openjdk-7-jre' 'openjdk-7-jdk' 'mysql-server*' 'libmysqlclient-dev' 'stress-ng' 'expect' 'bzr' 'libmysqld-dev' 'lshw' 'bridge-utils' 'dmidecode' 'lsdev' 'gfortran' 'numactl' 'unzip' 'bc' 'lksctp-tools' 'dstat' 'gcc-aarch64-linux-gnu')
    else
    	target_packages=('stress' 'make' 'build-essential' 'linux-tools-generic' 'linux-tools-common' 'gcc g++' 'nfs-common' 'automake' 'autoconf' 'autogen' 'libtool' 'openjdk-7-jre' 'openjdk-7-jdk' 'mysql-server*' 'libmysqlclient-dev' 'stress-ng' 'expect' 'bzr' 'libmysqld-dev' 'lshw' 'bridge-utils' 'dmidecode' 'lsdev' 'gfortran' 'numactl' 'unzip' 'bc' 'lksctp-tools' 'dstat')
    fi
    for i in `seq 0 $((${#target_packages[@]}-1)) `
    do
    #checking to see if all the target dependent packages are installed
        check=`dpkg-query -W -f='${Status}' ${target_packages[$i]} | grep -c "ok installed"`
        if [ $check -eq 0 ]
        then
            if [ $1 == "y" ]
            then
                choice="y"
            else
                echo -e "\n\t\t${target_packages[$i]} is not installed, would you like to install(y/n)"
                read choice
            fi

            if [ $choice == 'y' ]
            then
                if [ ${target_packages[$i]} == 'mysql-server*' -o ${target_packages[$i]} == 'libmysqlclient-dev' ]
                then
                    echo -e "$ERROR:The ${target_packages[$i]} package is not present. Please install it manually" >> target_dependency_output_summary.txt
                    continue
                else
                    sudo dpkg --configure -a
                    if [ $UPDATE=0 ]
                    then
                        UPDATE=1
                        sudo apt-get update
                    fi
                    sudo apt-get build-dep ${target_packages[$i]} -y
                    sudo apt-get install ${target_packages[$i]} -y
                    if [ $? -ne 0 ]
                    then
                        echo -e "\n\t\t$ERROR:${target_packages[$i]} is not installed properly" >> target_dependency_output_summary.txt
                        continue
		    else
			echo "${target_packages[$i]} is installed" >>  target_dependency_output_summary.txt
                    fi
                fi
            else
                echo "Please install ${target_packages[$i]} and try again" >> target_dependency_output_summary.txt
            fi
        else
           echo "${target_packages[$i]} is installed" >>  target_dependency_output_summary.txt
        fi
    done
else
    if [ ! $architecture_x86_64 -eq 0 ]
    then
        target_packages=('make' 'wget' 'gcc' 'automake' 'autoconf' 'cmake' 'net-tools' 'lshw' 'bridge-utils' 'java-1.8.0-openjdk.x86_64' 'java-1.8.0-openjdk-devel.x86_64' 'perl' 'lksctp-tools' 'expect' 'ncurses-devel' 'yum-utils' 'dmidecode' 'words' 'gfortran' 'numactl' 'unzip' 'bc' 'libtool' 'psmisc' 'dstat' 'gcc-c++' 'libaio' 'zlib.i686')
    else
        target_packages=('make' 'wget' 'gcc' 'automake' 'autoconf' 'cmake' 'net-tools' 'lshw' 'bridge-utils' 'java-1.8.0-openjdk.aarch64' 'java-1.8.0-openjdk-devel.aarch64' 'perl'  'lksctp-tools' 'expect' 'ncurses-devel' 'yum-utils' 'dmidecode' 'words' 'gfortran' 'numactl' 'unzip' 'bc' 'libtool' 'psmisc' 'dstat' 'gcc-c++' 'libaio')
    fi

    for i in `seq 0 $((${#target_packages[@]}-1)) `
    do
        #checking to see if all the target dependent packages are installed
        check=`rpm -qa ${target_packages[$i]}`
        if [  -z "$check" ]
        then
           if [ $1 == "y" ]
           then
               choice="y"
           else
               echo -e "\n\t\t${target_packages[$i]} is not installed, would you like to install(y/n)"
               read choice
           fi

           if [ $choice == 'y' ]
           then
                if [ $UPDATE=0 ]
                then
                    UPDATE=1
                    sudo yum update &
                    wait
                fi
                sudo yum-builddep -y ${target_packages[$i]} &
                wait
                sudo yum install -y ${target_packages[$i]} &
                wait
                if [ $? -ne 0 ]
                then
                        echo -e "\n\t\t$ERROR:${target_packages[$i]} is not installed properly" >>  target_dependency_output_summary.txt
                        continue
                fi
           else
               echo "Please install ${target_packages[$i]} and try again" >> target_dependency_output_summary.txt
           fi
        else
           echo "${target_packages[$i]} is installed" >> target_dependency_output_summary.txt
        fi
    done

	if [ $choice == 'y' ]
	then
                if [ ! `sudo find /usr/local/mysql/bin -name mysql` ];
		then
                        echo "install mysql-server manually..." >> target_dependency_output_summary.txt
		else
		        echo "mysql is installed" >> target_dependency_output_summary.txt
		fi
		if [ ! `sudo find /usr/local/bin -name stress` ];
		then
		        echo "installing stress..." >> target_dependency_output_summary.txt
		        cd /tmp
                        wget http://www.estuarydev.org/caliper/stress-1.0.4.tar.gz
		        sudo tar xvzf stress-1.0.4.tar.gz
		        cd stress-1.0.4
		        ./configure && sudo make && sudo make install
		else
		        echo "stress is installed" >>  target_dependency_output_summary.txt
		fi

		if [ ! `sudo find /usr/bin -name stress-ng` ];
		then
		        echo "installing stress-ng..." >> target_dependency_output_summary.txt
		        cd /tmp
                        wget http://www.estuarydev.org/caliper/stress-ng.zip
		        sudo unzip stress-ng.zip
		        cd stress-ng-master
		        sudo make && sudo make install
		else
		        echo "stress-ng is installed" >> target_dependency_output_summary.txt
		fi
	fi
fi
#mount a disk partition for storage testing
if [ ! -d "/mnt/sdb/" ]
then
    echo -e "\nCreating Mount Partition for fio testing\n"
    sudo mkdir -p /mnt/sdb/
        sudo chmod -R 775 /mnt/sdb
        sudo chown -R $USER:$USER /mnt/sdb
        sudo mount $2 /mnt/sdb
        if [ $? -ne 0 ]
        then
       echo -e "\n$ERROR:Creating a Mount Path for Fio testing Failed\n" >> target_dependency_output_summary.txt
    fi
else
        if [ `mount -l | grep -c "$2 on /mnt/sdb"` == 0 ]
        then
            sudo mount $2 /mnt/sdb
                if [ $? -ne 0 ]
                then
                echo -e "\n$ERROR:Creating a Mount Path for Fio testing Failed\n" >> target_dependency_output_summary.txt
            fi
        fi
        echo -e "\nMount Partition for storage testing Already exits\n" >> target_dependency_output_summary.txt
fi

#copying the perf 
if [ ! $Osname_Ubuntu -eq 0 ]
then
    temp=`ls -lt /usr/lib/linux-tools/ | head -n 2 | awk -F ' ' '{print $9}'`
    temp=${temp:1}
    cp /usr/lib/linux-tools/$temp/perf /usr/bin/
    if [ $? -ne 0 ]
    then
        echo -e "\n\t\t$ERROR:Failed to cp the perf path" >> target_dependency_output_summary.txt
    fi
fi

