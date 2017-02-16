#!/bin/bash

server_dependency="server_dependency_dir"

architecture_x86_64=`uname -a | grep -c "x86_64"`
architecture_arm64=`uname -a | grep -c "arm64"`

if [ ! -d $server_dependency ]
then
        sudo mkdir -p $server_dependency
fi
cd $server_dependency

file_present=server_dependency_output_summary.txt
if [ -f $file_present ]
then
    sudo rm server_dependency_output_summary.txt
fi

ERROR="ERROR-IN-AUTOMATION"
dependency=('netperf' 'iperf3' 'qperf')
UPDATE=0
flag=(1 1 1)
clear
echo "SERVER"
echo -e "\n\t\tServer Dependency"
for i in `seq 0 $((${#dependency[@]}-1)) `
do
	check=`sudo find /usr -name ${dependency[$i]} | grep -c ${dependency[$i]}`
        if [ $check -ne 0 ];then
            if [ ${dependency[$i]} == 'netperf' ];then 
		check_version=`netperf -V | grep -c "2.7.0"`
		if [ $check_version -eq 0 ];then
			echo "please install netperf 2.7.0 version" >> server_dependency_output_summary.txt
		fi
            elif [ ${dependency[$i]} == 'iperf3' ];then 
		check_version=`iperf3 --version | grep -c "3.1.4"`
		if [ $check_version -eq 0 ];then
			echo "please install iperf3 3.1.4 version" >> server_dependency_output_summary.txt
		fi
            elif [ ${dependency[$i]} == 'qperf' ];then 
		check_version=`qperf -V | grep -c "0.4.9"`
		if [ $check_version -eq 0 ];then
			echo "please install qperf 0.4.9 version" >> server_dependency_output_summary.txt
		fi
            fi
            echo -e "\n ${dependency[$i]} is already installed" >> server_dependency_output_summary.txt
    	else
	    # if force option is passed thn forcefully run the scripts
            if [ $1 = "y" ];then
                choice="y"
            else
                echo "${host_packages[$i]} is not installed, would you like to install(y/n)" >> server_dependency_output_summary.txt
	    fi
            if [ $choice == 'y' ];then
     		if [ ${dependency[$i]} == qperf ];then
                    wget https://www.openfabrics.org/downloads/qperf/qperf-0.4.9.tar.gz 
                    tar xvf qperf-0.4.9.tar.gz
                    cd qperf-0.4.9
		    if [ $architecture_x86_64 -eq 1 ];then
			./configure --build=x86_64-unknown-linux-gnu
		    elif [ $architecture_arm64 -eq 1 ];then
			./configure --build=aarch64-unknown-linux-gnu
		    fi
                    sudo make && sudo make install
		    cd ..
                elif [ ${dependency[$i]} == 'netperf' ];then
                     wget ftp://ftp.netperf.org/netperf/netperf-2.7.0.tar.gz
                     tar xf netperf-2.7.0.tar.gz
                     cd netperf-2.7.0
		     if [ $architecture_x86_64 -eq 1 ];then
			./configure --build=x86_64-unknown-linux-gnu
		     elif [ $architecture_arm64 -eq 1 ];then
			./configure --build=aarch64-unknown-linux-gnu
		     fi
                     sudo make && sudo make install
            	     sudo netserver
		     cd ..
		else
		     wget https://github.com/esnet/iperf/archive/3.1.4.zip
		     unzip 3.1.4.zip
		     cd iperf-3.1.4
    	             ./configure
		     make
		     sudo make install
		     cd ..
		fi
            fi
	fi
done

for i in `seq 0 $((${#flag[@]}-1)) ` 
do    
    j=${flag[$i]}
    if [ $j -eq 1 -a $i -eq 0 ];then
        if  ! ps -ef | grep "netserver" | grep -v grep ;then 
            echo -e "\n\t\tnetperf service not running"
            sudo netserver
            wait
            echo "\n\t\tdone restarting netperf"
            if [ $? -ne 0 ];then
                echo -e "\n\t\t$ERROR:Could Not restart Netperf please try again" >> server_dependency_output_summary.txt
                exit 1
            fi
        fi
    elif [ $j -eq 1 -a $i -eq 1 ];then
        if  ! ps -ef | grep "iperf3" | grep -v grep  ;then 
            iperf3 -s &
            if [ $? -ne 0 ];then
                echo -e "\n\t\t$ERROR:Could Not restart Iperf please try again" >> server_dependency_output_summary.txt
                exit 1
            fi
        fi
    elif [ $j -eq 1 -a $i -eq 2 ];then
        if  ! ps -ef | grep "qperf" | grep -v grep  ;then 
            qperf &
            if [ $? -ne 0 ];then
                echo -e "\n\t\t$ERROR:Could Not restart Qperf please try again" >> server_dependency_output_summary.txt
                exit 1
            fi
        fi
   fi         
done
